#!/usr/bin/env python3
import os
import shutil

import room
import scrape

def main():
    #scrape.scrape()
    rooms = room.load_from_json()
    rooms = list(filter(lambda r: r.court == 'Burrell\'s Field' and  r.room_type == 'Double', rooms))
    rooms.sort(key=lambda r: r.ensuite)
    rooms.sort(key=lambda r: r.number)
    rooms.sort(key=lambda r: r.staircase)

    links_dir = 'Filtered'
    os.makedirs(links_dir, exist_ok=True)
    for root, dirs, files in os.walk(links_dir):
        for f in files:
            os.unlink(os.path.join(root, f))
        for d in dirs:
            shutil.rmtree(os.path.join(root, d))

    for r in rooms:
        print(r)
        os.symlink(os.path.join(os.pardir, 'PDFs', r.get_pdf_path()), os.path.join(links_dir, r.get_pdf_filename()))

if __name__ == '__main__':
    try:
        os.chdir(os.path.expanduser('~/MyTrin Ballot'))
        main()
    except KeyboardInterrupt:
        pass
