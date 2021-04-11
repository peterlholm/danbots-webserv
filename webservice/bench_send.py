from datetime import datetime
from copy import deepcopy 
from io import BytesIO, open
from send_files import send_mem_files, send_mem_files_bg

antal=20
start = datetime.now()
with open('webservice.py', 'rb') as fh:
    myfd = BytesIO(fh.read())

for i in range(antal):
    # fd=BytesIO()
    # fd.write(myfd.getbuffer() )
    myfd.seek(0)
    newfd = deepcopy(myfd)
    RESULT = send_mem_files(newfd, "testfile"+str(i), file_type='py', info={'myinfo': 22}, params={'myparams':"parameter"})
    if not RESULT:
        print ("Noget gik galt")
    #send_mem_files_bg(newfd, "testfile"+str(i), file_type='py', info={'myinfo': 22}, params={'myparams':"parameter"})

slut = datetime.now()

print ("Transfers pr sek", antal/(slut-start).total_seconds())
