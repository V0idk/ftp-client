import socket
import os
import platform
import select


class FTP:
    socket_ftp = None
    socket_pasv = None
    targat_ip = ''
    targat_port = 21
    pasv_url = ''
    pasv_port = ''
    Login_or_not = False
    test_flag = False
    timeout = 3
    sys = platform.system()

    def inred(s):
        return"%s[31;2m%s%s[0m" % (chr(27), s, chr(27))

    def __init__(self, ip, port):
        self.targat_ip = ip
        self.targat_port = int(port)

    def inred(self, s):
        return "%s[31;2m%s%s[0m" % (chr(27), s, chr(27))

    def Help(self):
        print 'Command:\n' +\
              self.inred('     cd pathname \n') +\
              self.inred('     list\n') + \
              self.inred('     pwd\n') +\
              self.inred('     delete filename\n') +\
              self.inred('     quit \n') +\
              self.inred('     mkdir dirname\n') +\
              self.inred('     rmdir dirname\n') +\
              self.inred('     rename filename\n') +\
              self.inred('     size filename\n') +\
              self.inred('     download filename\n') +\
              self.inred('     upload filename\n') +\
              self.inred('     nlst:list current directoy content\n') +\
              self.inred('     multupload file1 file2 file3...\n') +\
              self.inred('     multdown file1 file2 file3...\n') +\
              self.inred('     multdel file1 file2 file3...\n') +\
              self.inred('     syst\n') +\
              self.inred('     type  [I|A]\n')

    def Parse_pasv_resp(self, content):
        if content[:3] != '227':
            print "Parse_pasv_resp error"
            return False
        l_pos = 0
        r_pos = 0
        '''
        227 Entering Passive Mode (192,168,1,102,16,157).
        '''
        for i in range(len(content)):
            if content[i] == '(':
                l_pos = i
            if content[i] == ')':
                r_pos = i
                break
        content = content[l_pos + 1: r_pos]
        item = content.split(',')
        self.pasv_url = item[0] + '.' + item[1] + '.' + item[2] + '.' + item[3]
        self.pasv_port = int(item[4]) * 256 + int(item[5])

    def Connect(self):
        #self.socket_ftp = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        try:
            self.socket_ftp = socket.create_connection(
                (self.targat_ip, self.targat_port), self.timeout)
        except socket.error, err:
            return False
        return True

    def Login(self, username, passwd):

        ready = select.select([self.socket_ftp], [], [], 0.5)

        self.socket_ftp.sendall('USER ' + username + '\r\n')
        if ready[0]:
            print self.socket_ftp.recv(1024)

        self.socket_ftp.sendall('PASS ' + passwd + '\r\n')
        if ready[0]:
            print self.socket_ftp.recv(1024)

        try:
            if ready[0]:
                cmd = self.socket_ftp.recv(1024)
                print cmd
        except socket.timeout:
            self.socket_ftp.sendall('SYST' + '\r\n')
            if self.socket_ftp.recv(1024).find('215') != -1:
                self.Login_or_not = True
                return True
            else:
                print 'Login failed'
                return False

        if cmd.find("230") == -1:  # 230 User logged in success
            print 'Login failed'
            return False

        self.Login_or_not = True
        return True

    def Is_login(self):
        if self.Login_or_not == False:
            print "permission denied, please Login!"
            return False
        return True

    def Pasv(self):
        if self.Is_login() == False:
            return False
        self.socket_ftp.sendall('PASV\r\n')
        cmd = self.socket_ftp.recv(1024)
        self.Parse_pasv_resp(cmd)
        try:
            self.socket_pasv = socket.create_connection(
                (self.pasv_url, self.pasv_port))
        except socket.error, err:
            self.Pasv()
        return True

    def Cd(self, path):
        if self.Is_login() == False:
            return
        temp = "CDUP" + '\r\n'
        if path == '..':
            temp = "CDUP" + '\r\n'
        else:
            temp = 'CWD ' + path + '\r\n'
        self.socket_ftp.sendall(temp)
        cmd = self.socket_ftp.recv(1024)
        if self.test_flag == False:
            print cmd
        if cmd.find("250") == -1:  # 250 Requested file action okay, complete
            return False
        return True

    def GetSize(self, filename):
        if self.Is_login() == False:
            return
        self.socket_ftp.sendall("SIZE " + filename + '\r\n')
        cmd = self.socket_ftp.recv(1024)
        if self.test_flag == False:
            print cmd
        if cmd.find('213') == -1:  # if not 213 ,error
            return -1
        else:
            size = cmd.split(" ")
            return int(size[1])

    def List(self, pathname=''):
        if self.Is_login() == False:
            return

        self.Pasv()
        self.socket_ftp.sendall('LIST '+pathname + '\r\n')
        cmd = self.socket_ftp.recv(1024)
        if cmd.find("150") == -1:  # 150 File status okay;
            print cmd
            return
        content = self.socket_pasv.recv(8192)
        print content
        self.socket_pasv.close()

        ready = select.select([self.socket_ftp], [], [], 0.5)
        if ready[0]:
            cmd = self.socket_ftp.recv(1024)

        '''
        self.socket_ftp.settimeout(0.5)
        try:
          cmd = self.socket_ftp.recv(1024)
        except socket.timeout:
        	pass
        self.socket_ftp.settimeout(None)
        print cmd
        '''

        if cmd.find("226") == -1:  # 126 Closing data connection
            print cmd
            return False
        print cmd
        return True

    def Nlst(self):
        if self.Is_login() == False:
            return
        self.Pasv()
        self.socket_ftp.sendall('NLST' + '\r\n')
        cmd = self.socket_ftp.recv(1024)
        if cmd.find("150") == -1:  # 150 File status okay;
            print cmd
        content = self.socket_pasv.recv(8096)
        if self.test_flag == False:
            print content
        self.socket_pasv.close()

        ready = select.select([self.socket_ftp], [], [], 0.5)
        if ready[0]:
            cmd = self.socket_ftp.recv(1024)
        '''
        self.socket_ftp.settimeout(0.5)
        try:
          cmd = self.socket_ftp.recv(1024)
        except socket.timeout:
        	pass
        self.socket_ftp.settimeout(None)
        print cmd
        '''

        if cmd.find("226") == -1:  # 126 Closing data connection
            print cmd
            return ""
        print cmd
        return content

    def RuturnPWDFilelist(self):
        filelist = self.Nlst().split('\r\n')[2:][: -1]
        return filelist

    def Multdel(self, dirname):
        self.test_flag = True

        pwd = self.Pwd()
        if self.Cd(dirname) == False:
            self.test_flag = False
            self.Delete(dirname)
            self.test_flag = True
            return
        filelist = self.RuturnPWDFilelist()
        for file in filelist:
            self.Multdel(file)

        self.Cd(pwd)
        self.test_flag = False
        self.Rmdir(dirname)

    def Multdown(self, dirname):
        self.test_flag = True

        pwd = self.Pwd()
        if self.Cd(dirname) == False:
            self.Download(dirname, dirname)
            return
        os.mkdir(dirname)
        os.chdir(dirname)
        filelist = self.RuturnPWDFilelist()
        for file in filelist:
            self.Multdown(file)

        self.Cd(pwd)
        os.chdir("..")
        self.test_flag = False

    def Multupload(self, dirname):
        self.test_flag = True
        pwd = self.Pwd()
        pwd2 = os.getcwd()
        if os.path.isdir(dirname) == False:
            self.Upload(dirname, dirname)
            return
        os.chdir(dirname)
        self.Mkdir(os.path.basename(dirname))
        self.Cd(os.path.basename(dirname))
        filelist = os.listdir('.')
        for file in filelist:
            self.Multupload(file)

        self.Cd(pwd)
        os.chdir(pwd2)
        self.test_flag = False

    def Download(self, filein, fileout, offset=0):
        if self.Is_login() == False:
            return False

        if offset == 0:
            self.Pasv()
        self.socket_ftp.sendall('RETR ' + filein + '\r\n')
        cmd = self.socket_ftp.recv(1024)

        if cmd.find("150") == -1:  # File status okay;
            print cmd
            return False
        print cmd
        self.test_flag = True
        size = self.GetSize(filein)  # print file size again
        self.test_flag = False
        size -= offset
        fileout_p = None
        if offset == 0:
            fileout_p = open(fileout, "wb")
        else:
            fileout_p = open(fileout, "ab+")

        while 1:
            data = self.socket_pasv.recv(1024)
            if not data:
                break
            fileout_p.write(data)

        fileout_p.close()
        self.socket_pasv.close()

        ready = select.select([self.socket_ftp], [], [], 0.5)
        if ready[0]:
            cmd = self.socket_ftp.recv(1024)
        '''
        self.socket_ftp.settimeout(1.0)
        try:
          cmd = self.socket_ftp.recv(1024)
        except socket.timeout:
        	pass

        self.socket_ftp.settimeout(None)
        '''
        print cmd

        if cmd.find("226") == -1:
            return False
        else:
            return True

    def Upload(self, filein, fileout):
        if self.Is_login() == False:
            return False

        self.Pasv()
        self.socket_ftp.sendall('STOR ' + fileout + '\r\n')
        cmd = self.socket_ftp.recv(1024)
        if cmd.find("150") == -1:
            print cmd
            return False

        file_p = open(filein, "rb")
        self.socket_pasv.sendall(file_p.read())
        file_p.close()
        self.socket_pasv.close()

        cmd = self.socket_ftp.recv(1024)
        print cmd
        if cmd.find("226") == -1:
            return False
        return True

    def ReDownload(self, filein, fileout, offset):
        if self.Is_login() == False:
            return False

        self.Pasv()
        self.socket_ftp.sendall('REST ' + str(offset) + '\r\n')
        cmd = self.socket_ftp.recv(1024)
        print cmd

        if cmd.find("350") == -1:  # Requested file action pending further informatio
            print cmd
            return False

        self.Download(filein, fileout, offset)

    def Rename(self, oldname, newname):
        if self.Is_login() == False:
            return False
        self.socket_ftp.sendall('RNFR ' + oldname + '\r\n')
        print self.socket_ftp.recv(1024)
        self.socket_ftp.sendall('RNTO ' + newname + '\r\n')
        print self.socket_ftp.recv(1024)

    def Rmdir(self, dirname):
        if self.Is_login() == False:
            return False
        self.socket_ftp.sendall('RMD ' + dirname + '\r\n')
        print self.socket_ftp.recv(1024)

    def Quit(self):
        if self.Is_login() == False:
            return False
        self.socket_ftp.sendall('QUIT' + '\r\n')
        print self.socket_ftp.recv(1024)
        self.socket_ftp.close()

    def Delete(self, filename):
        if self.Is_login() == False:
            return False
        self.socket_ftp.sendall('DELE ' + filename + '\r\n')
        print self.socket_ftp.recv(1024)

    def Mkdir(self, dirname):
        if self.Is_login() == False:
            return False
        self.socket_ftp.sendall('MKD ' + dirname + '\r\n')
        print self.socket_ftp.recv(1024)

    def Pwd(self):
        if self.Is_login() == False:
            return False
        self.socket_ftp.sendall('PWD' + '\r\n')
        content = self.socket_ftp.recv(1024)
        if self.test_flag == False:
            print content
        l_pos = 0
        r_pos = 0
        '''
        257 "/" is current directory.
        '''
        for i in range(5, len(content)):
            if content[i] == '"':
                r_pos = i
                break
        return content[5: r_pos]

    def Syst(self):
        if self.Is_login() == False:
            return False
        self.socket_ftp.sendall('SYST' + '\r\n')
        print self.socket_ftp.recv(1024)

    def Type(self, mode):
        if self.Is_login() == False:
            return False
        self.socket_ftp.sendall('TYPE ' + mode + '\r\n')
        print self.socket_ftp.recv(1024)
