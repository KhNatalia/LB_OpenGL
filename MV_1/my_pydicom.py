import pydicom as dicom

my_file = dicom.read_file("FluroWithDisplayShutter.dcm")
print(my_file)
