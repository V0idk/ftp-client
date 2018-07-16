from ftp import FTP
import os

con_ = False
login_ = False

while True:

    while con_ == False:
        ip_port = raw_input('input (IP:port) : ')
        ip_port_list = ip_port.split(':')
        try:
            ip = ip_port_list[0]
            port = ip_port_list[1]
        except IndexError:
            print 'illegal input!Check'
            continue
        myftp = FTP(ip, port)
        if myftp.Connect() == False:
            print "Error,check target IP"
            continue
        else:
            con_ = True

    while login_ == False:
        username = raw_input('Username: ')
        passwd = raw_input('Password: ')
        if myftp.Login(username, passwd) == False:
            continue
        else:
            login_ = True

    while True:
        cmd = raw_input('ftp > ')

        if cmd[0: 4] == "list":
            myftp.List(cmd[5:])

        if cmd[0: 8] == "download":
            filein = cmd[9:]
            fileout = raw_input("Input local filename to store: ")
            myftp.Download(filein, fileout)

        if cmd[0: 6] == "upload":
            filein = cmd[7:]
            fileout = raw_input("Input remote filename to store: ")
            myftp.Upload(filein, fileout)

        if cmd[0: 10] == "redownload":
            filein = cmd[11:]
            fileout = raw_input("Input the original filename: ")
            size = os.path.getsize(fileout)
            myftp.ReDownload(filein, fileout, size)

        if cmd[0: 2] == "cd":
            path = cmd[3:]
            myftp.Cd(path)

        if cmd[0: 4] == "size":
            filename = cmd[5:]
            print filename + "'s size is " + \
                str(myftp.GetSize(filename)) + " bytes"

        if cmd[0: 6] == "rename":
            oldname = cmd[7:]
            newname = raw_input("please input the new name: ",)
            myftp.Rename(oldname, newname)

        if cmd[0: 5] == "rmdir":
            dirname = cmd[6:]
            myftp.Rmdir(dirname)

        if cmd[0: 4] == "quit":
            con_ = False
            login_ = False
            myftp.Quit()
            break

        if cmd[0: 6] == "delete":
            filename = cmd[7:]
            myftp.Delete(filename)

        if cmd[0: 5] == "mkdir":
            dirname = cmd[6:]
            myftp.Mkdir(dirname)

        if cmd[0: 3] == "pwd":
            myftp.Pwd()

        if cmd[0: 4] == "help":
            myftp.Help()

        if cmd[0: 4] == "nlst":
            path = cmd[5:]
            myftp.Nlst()
        if cmd[0: 7] == "multdel":
            item = cmd.split(' ')[1:]
            for filename in item:
                myftp.Multdel(filename)

        if cmd[0: 8] == "multdown":
            item = cmd.split(' ')[1:]
            for filename in item:
                try:
                    myftp.Multdown(filename)
                except IOError:
                    print 'IO ERROR'
                    continue

        if cmd[0: 10] == "multupload":
            item = cmd.split(' ')[1:]
            for filename in item:
                try:
                    myftp.Multupload(filename)
                except IOError:
                    print 'IO ERROR'
                    continue

        if cmd[0: 4] == "syst":
            myftp.Syst()

        if cmd[0:4] == 'type':
            myftp.Type(cmd[5])
