import configparser
import os.path


def parseLicence(path):
    licence = {}
    config = configparser.ConfigParser()
    lic_list = config.read(path)
    if lic_list == []:
        return licence

    if config.has_section('Licence'):
        licence['ID'] = config['Licence'].get('ID')
        licence['PW'] = config['Licence'].getint('PW')
        return licence

def identifyUser(licence):
    if licence == {}:
        return 'Default'
    password = hex(licence['PW'])
    if licence['ID'] == 'Kaikutek':
        if password[-3:] in ['dad'] or password =='0x32195a8':
            return 'Developer'
        elif password[-3:] in ['fae']:
            return 'FAE'
    elif licence['ID'] == 'Costumer':
        if password[-3:] in ['dad'] or password == '0x32195a8':
            return 'Costumer'
    return 'Default'


if __name__ == '__main__':
    from KKT_Module.ksoc_global import kgl
    license = parseLicence(os.path.join(kgl.KKTConfig,'Licence.ini'))
    User = identifyUser(license)
    print(User)