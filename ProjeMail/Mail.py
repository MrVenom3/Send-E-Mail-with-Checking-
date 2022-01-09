import sys
import re
import os
from PyQt5.QtCore import QRect, QSize
from PyQt5.QtGui import *
from PyQt5.QtWidgets import *
from PyQt5.QtCore import Qt
import source

import smtplib, ssl
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText as text

from Tkinter import *

from tkSimpleDialog import askstring

from tkFileDialog   import asksaveasfilename
from tkFileDialog import askopenfilename

from tkMessageBox import askokcancel

Window = Tk()
Window.title("TekstEDIT")
index = 0

class Editor(ScrolledText):

    Button(frm, text='Night-Mode',  command=self.onNightMode).pack(side=LEFT)

    def onNightMode(self):
        if index:
            self.text.config(font=('courier', 12, 'normal'), background='black', fg='green')

        else:
            self.text.config(font=('courier', 12, 'normal'))

        index = not index
        else:
        self.text.config(font=('courier', 12, 'normal'), background='green', fg='black')

class MainWindow(QMainWindow):
    def __init__(self):
        QMainWindow.__init__(self)
        self.setWindowIcon(QIcon(':/img/Iconlar/arama.png'))
        self.setStyleSheet("QMainWindow{border-image:url(:/img/Iconlar/arkaplan.jpg) 0 0 0 0 stretch stretch}")
        self.setFixedSize(QSize(600, 400))
        self.setWindowTitle("Python Kişisel Bilgileri Koruma")

        self.lblMail = QLabel(self)
        self.lblMail.setText("Mail'in gönderileceği E-Posta adresi:")
        self.lblMail.setGeometry(QRect(30, 10, 300, 30))
        self.lblMail.setStyleSheet("color:white; font-weight: bold")

        self.txtMailAdresi = QLineEdit(self)
        self.txtMailAdresi.setGeometry(QRect(30, 40, self.width()-150, 37))

        self.txtMailBaslik = QLineEdit(self)
        self.txtMailBaslik.setGeometry(QRect(int((self.width()-300)/2),85,300, 37))
        self.txtMailBaslik.setPlaceholderText("BAŞLIK")

        self.lblMesaj=QLabel("Mesajınız:", self)
        self.lblMesaj.setGeometry(QRect(30,130,300,30))
        self.lblMesaj.setStyleSheet("color:white; font-weight: bold")

        self.txtMailMesaj = QLineEdit("45223860178",self)
        self.txtMailMesaj.setGeometry(QRect(30, 160, self.width() - 60, self.height()-170))
        self.txtMailMesaj.setAlignment(Qt.AlignTop | Qt.AlignLeft)

        self.btnGonder = QPushButton("Gönder", self)
        self.btnGonder.setGeometry(QRect(self.width()-110, 40,80,37))
        self.btnGonder.setStyleSheet("""QPushButton{color:white;}QPushButton:pressed 
                {background-color:blue(spread:pad, x1:0, y1:0, x2:0, y2:1,   
                stop:0 rgba(80, 175, 162, 255),  stop:1 rgba(98, 211, 162, 255))}QPushButton 
                {     background-color: rgb(61, 204, 199, 200); 
                border: 1px solid black;     border-radius: 5px;}""")


        self.btnGonder.setFont(QFont('Arial',12))

        self.txtMailAdresi.setFont(QFont('Arial', 12))
        self.btnGonder.clicked.connect(self.Gonder)

        self.show()

    def Dogrula_TC(self, TC):
        value = str(TC)
        if not len(value) == 11: # 11 haneli degilse
            return False

        if not value.isdigit(): # rakamdan olusmuyorsa
            return False

        if int(value[0]) == 0: # ilk rakam 0 ise
            return False

        digits = [int(d) for d in str(value)] # int liste

        # 1. 2. 3. 4. 5. 6. 7. 8. 9. ve 10. hanelerin toplamından elde edilen sonucun
        # 10'a bölümünden kalan, yani Mod10'u bize 11. haneyi verir.
        if not sum(digits[:10]) % 10 == digits[10]:
            return False

        if not (((7 * sum(digits[:9][-1::-2])) - sum(digits[:9][-2::-2])) % 10) == digits[9]:
            return False
        return True
    def Gonder(self):
        try:
            MailAdresi=self.txtMailAdresi.text()
            Mesaj = self.txtMailMesaj.text()  # Kullanicinin girecegi mesaji Mesaj degiskenine string olarak aliyoruz
            Baslik = self.txtMailBaslik.text()
            if (MailAdresi =="" or Mesaj=="" or Baslik==""):
                self.msgHata("Lütfen Mail Adresinin, Başlığın ve Mesaj kısmının dolu olduğuna emin olun.")
                return

            OLASI_tcno = re.findall("[1-9]{1}[0-9]{10}",Mesaj)
            OLASI_kredino = re.findall("(?:5[1-5][0-9]{2}|222[1-9]|22[3-9][0-9]|2[3-6][0-9]{2}|27[01][0-9]|2720)[0-9]{12}", Mesaj)
            TCLER=[]
            TANE_TC= len(OLASI_kredino)# 0
            TANE_KREDIKARTI=0
            for tc in OLASI_tcno:
                if self.Dogrula_TC(tc):
                    TCLER.append(tc)
                    TANE_TC+=1


            if TANE_TC == 0 and TANE_KREDIKARTI==0:
                if self.MailGonder(MailAdresi, Baslik, Mesaj):
                    self.msgBasarili("Mail Başarıyla Gönderildi!")
                else:
                    self.msgHata("Mail Gönderilemedi!")
            else:
                gosterilecekMesaj="\t---- BİLGİLERİNİZ ----<br>"
                if TANE_TC > 0:
                    gosterilecekMesaj += "TC Kimlik: <font color='red'>%d</font><br>" % (TANE_TC)
                if TANE_KREDIKARTI > 0:
                    gosterilecekMesaj += "Kredi Kartı: <font color='red'>%d</font><br>" % (TANE_KREDIKARTI)

                if self.msgYesNoUyariSoru("UYARI", gosterilecekMesaj+"<br>Adet Özel bilgileriniz bulunuyor.<br>Güvenliğiniz için özel bilgilerinizi göndermemenizi öneririz.<br><br>Yine de devam etmek istiyor musunuz?"):
                    if self.MailGonder(MailAdresi, Baslik, Mesaj):
                        self.msgBasarili("Mail Başarıyla Gönderildi!")
                    else:
                        self.msgHata("Mail Gönderilemedi!")

            #print("%s - %s" % (str(OLASI_kredino), str(TCLER)))
        except Exception as err:
            print('Gonder Hata: %s' %str(err))
            self.debugHataPrint()


    def MailGonder(self, Adres, Baslik, Mesaj):
        try:
            smtp_server = "smtp.gmail.com"
            port = 587
            gonderici_Email = "beykoz.proje1@gmail.com"
            gonderici_Sifre="beykoz123458."
            context = ssl.create_default_context()

            msg = text(Mesaj)
            msg['From'] = gonderici_Email
            msg['To'] = Adres
            msg['Subject'] = Baslik


            server = smtplib.SMTP(smtp_server, port)
            server.ehlo()
            server.starttls(context=context)
            server.ehlo()
            server.login(gonderici_Email, gonderici_Sifre)
            server.sendmail(gonderici_Email, Adres, msg.as_string())

            server.quit()
            return True
        except Exception as err:
            print("MailGonder err: %s" % str(err))
            self.debugHataPrint()
            return False


    def msgBasarili(self, mesaj):
        msg = QMessageBox()
        msg.setWindowIcon(QIcon(':/img/Iconlar/arama.png'))
        msg.setIconPixmap(QIcon(':/img/Iconlar/basarili.png').pixmap(QSize(64, 64)))
        msg.setText(mesaj)
        msg.setWindowTitle("Başarılı")
        msg.exec()


    def msgHata(self, mesaj):
        msg = QMessageBox()
        msg.setWindowIcon(QIcon(':/img/Iconlar/arama.png'))
        msg.setIcon(QMessageBox.Critical)
        msg.setText(mesaj)
        msg.setWindowTitle("Hata")
        msg.exec()

    def msgYesNoUyariSoru(self, baslik, mesaj):
        msgBox = QMessageBox(self)
        msgBox.setFont(QFont('Arial', 12, weight=QFont.Bold))
        msgBox.setWindowTitle(baslik)
        msgBox.setText(mesaj)
        msgBox.setWindowIcon(QIcon(':/img/Iconlar/arama.png'))
        msgBox.setStandardButtons(QMessageBox.Yes)
        msgBox.addButton(QMessageBox.No)
        buttonY = msgBox.button(QMessageBox.Yes)
        buttonY.setText('Evet')
        buttonX = msgBox.button(QMessageBox.No)
        buttonX.setText('Hayır')
        if msgBox.exec() == QMessageBox.Yes:
            return True
        else:
            return False

    def debugHataPrint(self):
        exc_type, exc_obj, exc_tb = sys.exc_info()
        fname = os.path.split(exc_tb.tb_frame.f_code.co_filename)[1]
        print(exc_type, fname, exc_tb.tb_lineno)


if __name__ == "__main__":
    app = QApplication(sys.argv)
    anapencere = MainWindow()
    desktop = QApplication.desktop()

    pencere_genislik = desktop.width()
    pencere_uzunluk = desktop.height()
    anapencere.move((pencere_genislik - anapencere.width()) / 2, (pencere_uzunluk - anapencere.height()) / 2)
    sys.exit(app.exec_())