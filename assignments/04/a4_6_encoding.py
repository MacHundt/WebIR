
from os import listdir
from os.path import isfile, join
from chardet.universaldetector import UniversalDetector

__author__ = 'Bassel Khatib & Michael Hundt'

if __name__ == '__main__':
    path_in = "./input/"
    path_out = "./output/"
    targetEncoding = "utf-8"

    onlyfiles = [f for f in listdir(path_in) if isfile(join(path_in, f))]
    detector = UniversalDetector()

    for file_path in onlyfiles:
        print(file_path.ljust(60))
        detector.reset()
        for line in open(path_in+file_path, 'rb'):
            detector.feed(line)
            if detector.done:
                break
        detector.close()
        print(detector.result)

        sourceEncoding = detector.result['encoding']
        source = open(path_in+file_path, 'rb')
        target = open(path_out+file_path+"_utf-8", "w")

        for line in source.readlines():
            udata = line.decode(sourceEncoding)
            data = udata.encode(targetEncoding, "ignore")
            target.write(str(data)+'\n')
        target.close()


