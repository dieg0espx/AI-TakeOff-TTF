import os
from lxml import etree

# List of target path IDs
# paths = [
#     'path3900', 'path3910', 'path3920', 'path3930', 'path4514', 'path4516', 'path6792', 'path6782',
#     'path6802', 'path6842', 'path6844', 'path7336', 'path7338', 'path7352', 'path7654', 'path7664',
#     'path7674', 'path7692', 'path7850', 'path7852', 'path7914', 'path7924', 'path7934', 'path7944',
#     'path8414', 'path8458', 'path8460', 'path9776'
# ]
paths = [
    'path2864',
    'path2866',
    'path2868',
    'path2870',
    'path2872',
    'path2874',
    'path2876',
    'path2878',
    'path2880',
    'path2882',
    'path2884',
    'path2886',
    'path2920',
    'path2922',
    'path2924',
    'path2926',
    'path2928',
    'path2930',
    'path2932',
    'path2934',
    'path2936',
    'path2938',
    'path2940',
    'path2942',
    'path3740',
    'path3742',
    'path3744',
    'path3746',
    'path3748',
    'path3750',
    'path3896',
    'path3898',
    'path3902',
    'path3904',
    'path3906',
    'path3908',
    'path3912',
    'path3914',
    'path3916',
    'path3918',
    'path3922',
    'path3924',
    'path3926',
    'path3928',
    'path3932',
    'path3934',
    'path6454',
    'path6456',
    'path6458',
    'path6460',
    'path6462',
    'path6464',
    'path6778',
    'path6780',
    'path6784',
    'path6786',
    'path6788',
    'path6790',
    'path6794',
    'path6796',
    'path6798',
    'path6800',
    'path6804',
    'path6806',
    'path6818',
    'path6820',
    'path6822',
    'path6824',
    'path6826',
    'path6828',
    'path6830',
    'path6832',
    'path6834',
    'path6836',
    'path6838',
    'path6840',
    'path7328',
    'path7330',
    'path7332',
    'path7334',
    'path7340',
    'path7342',
    'path7344',
    'path7346',
    'path7348',
    'path7350',
    'path7354',
    'path7356',
    'path7650',
    'path7652',
    'path7656',
    'path7658',
    'path7660',
    'path7662',
    'path7666',
    'path7668',
    'path7670',
    'path7672',
    'path7676',
    'path7678',
    'path7688',
    'path7690',
    'path7694',
    'path7696',
    'path7826',
    'path7828',
    'path7830',
    'path7832',
    'path7834',
    'path7836',
    'path7838',
    'path7840',
    'path7842',
    'path7844',
    'path7846',
    'path7848',
    'path7910',
    'path7912',
    'path7916',
    'path7918',
    'path7920',
    'path7922',
    'path7926',
    'path7928',
    'path7930',
    'path7932',
    'path7936',
    'path7938',
    'path7940',
    'path7942',
    'path7946',
    'path7948',
    'path8010',
    'path8012',
    'path8016',
    'path8018',
    'path8434',
    'path8436',
    'path8438',
    'path8440',
    'path8442',
    'path8444',
    'path8446',
    'path8448',
    'path8450',
    'path8452',
    'path8454',
    'path8456',
    'path9772',
    'path9774',
    'path9778',
    'path9780'
]


def find_matching_paths(svg_path):
    if not os.path.exists(svg_path):
        print("Error: File not found!")
        return

    print(f"Analyzing SVG file: {svg_path}")

    # Parse SVG
    parser = etree.XMLParser(remove_blank_text=True)
    tree = etree.parse(svg_path, parser)
    root = tree.getroot()

    # Find all <path> elements
    count = 0
    for path in root.xpath("//*[local-name()='path']"):
        
        path_id = path.get("id")
        d_attr = path.get("style")

        if path_id in paths and d_attr:
            count = count + 1
            print(f"{path_id}: {d_attr}")

if __name__ == "__main__":
    svg_file = "local_file.svg"  # Change this if the file is in a different location
    find_matching_paths(svg_file)
