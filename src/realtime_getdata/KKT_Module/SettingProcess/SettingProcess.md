## Phase Calibration

---
* **AI mux and Tracking mux raw data compensate to HW address**

下表中 "adc_ch1" 代表的是 RX1 的 raw data，所以當值填0的時候
，channel 1 的 raw data 會是 RX1(adc_ch1) 的 raw data，channel 2 的 raw data 會是 RX2(adc_ch2) 的 raw data。

````
Select two channel data
0 = 4’b0000: adc_ch1, adc_ch2
1 = 4’b0001: adc_ch2, adc_ch3
2 = 4’b0010: adc_ch3, adc_ch1
3 = 4’b0011: adc_ch1, adc_ch1
4 = 4’b0100: adc_ch2, adc_ch1
5 = 4’b0101: adc_ch3, adc_ch2
6 = 4’b0110: adc_ch1, adc_ch3
7 = 4’b0111: adc_ch2, adc_ch2
8 = 4'b1000: adc_ch3, adc_ch3
````
根據圖上的規則 AI MUX 會根據不同 MUX 值讓不同的 RX 的 raw data 進去 channel 1 和 
channel 2 做計算， Tracking MUX 同理。 由 RX raw data 進入的 channel 可以知道三個 RX 
的 compensate 值要填在哪個 address。

AI MUX 的 CH1 CH2 填入 `$DSPRx20M_Unit_0`
* CH1 -> `0x400D200C`
* CH2 -> `0x400D600C`

Tracking MUX 只填 CH1 的 compensate 在 `$DSPRx20M_Unit_1`
* CH1 -> `0x400F200C`。

![示意圖](.\MD_images\Mux.png)

```python
    _block_select_table = dict(enumerate(
        ((0b001, 0b010),
         (0b010, 0b100),
         (0b100, 0b001),
         (0b001, 0b001),
         (0b010, 0b001),
         (0b100, 0b010),
         (0b001, 0b100),
         (0b010, 0b010),
         (0b100, 0b100),)
    ))
```
`_block_select_table`為參照上表的 dictionary, `0b001`表示 raw data 來自 RX1。

由 `AI MUX`及 `Tracking MUX`的值就可以知道 compensate要填在哪個 HW address。
```python
    # default compensates
    unit0_upper_real_compensate = 1024
    unit0_upper_image_compensate = 0
    unit0_lower_real_compensate = 1024
    unit0_lower_image_compensate = 0
    unit1_upper_real_compensate = 1024
    unit1_upper_image_compensate = 0

    # 從dictionary 中取得 ch1 ch2 是 RX 幾的 raw data
    AI_block_select = self._block_select_table.get(int(AI_mux)) 
    tracking_block_select = self._block_select_table.get(int(tracking_mux))

    if AI_block_select[0] & 0b1: # ch1 raw data is from RX1
        unit0_upper_real_compensate = RX1_real_compensate
        unit0_upper_image_compensate = RX1_image_compensate
    elif AI_block_select[0] & 0b10:# ch1 raw data is from RX2
        unit0_upper_real_compensate = RX2_real_compensate
        unit0_upper_image_compensate = RX2_image_compensate

    kgl.ksoclib.writeReg(unit0_upper_real_compensate, 0x400D200C, 11, 0)
    kgl.ksoclib.writeReg(unit0_upper_image_compensate, 0x400D200C, 23, 12)

    if AI_block_select[1] & 0b1:# ch2 raw data is from RX1
        unit0_lower_real_compensate = RX1_real_compensate
        unit0_lower_image_compensate = RX1_image_compensate
    elif AI_block_select[1] & 0b10:# ch2 raw data is from RX2
        unit0_lower_real_compensate = RX2_real_compensate
        unit0_lower_image_compensate = RX2_image_compensate

    kgl.ksoclib.writeReg(unit0_lower_real_compensate, 0x400D600C, 11, 0)
    kgl.ksoclib.writeReg(unit0_lower_image_compensate, 0x400D600C, 23, 12)

    if tracking_block_select[0] & 0b1:# ch1 raw data is from RX1
        unit1_upper_real_compensate = RX1_real_compensate
        unit1_upper_image_compensate = RX1_image_compensate
    elif tracking_block_select[0] & 0b10:# ch1 raw data is from RX2
        unit1_upper_real_compensate = RX2_real_compensate
        unit1_upper_image_compensate = RX2_image_compensate

        kgl.ksoclib.writeReg(unit1_upper_real_compensate, 0x400F200C, 11, 0)
        kgl.ksoclib.writeReg(unit1_upper_image_compensate, 0x400F200C, 23, 12)
```
* **Opened RX relation with ADC_Mux parameters**

根據 RF 的設定開啟的 RX 以及`_block_select_table`來設定 `AI MUX` 及 `Tracking MUX`的值。

**default mux**

* Open RX13  -> (6, 6)
* Open RX23  -> (1, 1)
* Open RX3   -> (8, 8)
* Open RX123 -> (0, 8)

```python
    # get enable block select number
    block_select =[]
    for k , v in cls._block_select_table.items():
        if open_RX | (v[0] | v[1]) == open_RX:
            block_select.append(k)

    AI_mux = kwargs.get('AI_mux', False)
    tracking_mux = kwargs.get('tracking_mux', False)

    # set default mux
    if open_RX == 0b101: # open RX13
        if AI_mux is False:
            AI_mux = 6
        if tracking_mux is False:
            tracking_mux = 6
    elif open_RX == 0b110:# open RX23
        if AI_mux is False:
            AI_mux = 1
        if tracking_mux is False:
            tracking_mux = 1
    elif open_RX == 0b100:# open RX3
        if AI_mux is False:
            AI_mux = 8
        if tracking_mux is False:
            tracking_mux = 8
    elif open_RX == 0b111:# open RX123
        if AI_mux is False:
            AI_mux = 0
        if tracking_mux is False:
            tracking_mux = 8
    else:
        raise Exception('Open RX mode is not enable !')

    assert (AI_mux in block_select),'input AI_mux = {} is not available!'.format(AI_mux)
    assert (tracking_mux in block_select),'input tracking_mux = {} is not available!'.format(tracking_mux)
```

設定 `tracking enable` ,`tracking enable`的值為開啟RX的數量。

```python 
  # set tracking enable = number of open RX
    tracking_enable = kwargs.get('tracking_enable', False)
    if not tracking_enable:
    tracking_enable = (open_RX & 0b1) + ((open_RX>>1) & 0b1) +((open_RX>>2) & 0b1 )
```
設定 `dim_sel` ,`dim_sel`的值為開啟RX的數量-1，若開啟 RX123 且為 `TDD`模式則 dim_sel = 3。
```python
    # set dim select
    dim_sel = kwargs.get('dim_sel', False)
    if not dim_sel:
        dim_sel = tracking_enable - 1
    # if TDD mode must enable all RX and dim_sel = 3
    if  kgl.ksoclib.readReg(0x50000548, 8, 8) and dim_sel==2:
        dim_sel += 1
```
設定 `channel_valid`， `channel_valid`為 bit enable的形式，ex. open RX13 channel_valid = `0b101`

```python
    # set channel valid
    Ch_valid = kwargs.get('Ch_valid', False)
    if not Ch_valid:
        Ch_valid = open_RX
```