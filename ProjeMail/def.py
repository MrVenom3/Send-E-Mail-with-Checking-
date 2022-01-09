import sys
import re
import os
from PyQt5.QtCore import QRect, QSize
from PyQt5.QtGui import *
from PyQt5.QtWidgets import *
from PyQt5.QtCore import Qt
import json
import source

import smtplib, ssl
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText as text

class MainWindow(QMainWindow):
    YoneticiMail=""
    Karanlik=False
    def __init__(self):
        QMainWindow.__init__(self)
        self.setWindowIcon(QIcon(':/img/Iconlar/arama.png'))
        self.setStyleSheet("QMainWindow{border-image:url(:/img/Iconlar/acik.png) 0 0 0 0 stretch stretch}")
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

        self.txtMailMesaj = QLineEdit("",self)
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
        self.btnAyarlar=QPushButton("Ayarlar", self)
        self.btnAyarlar.clicked.connect(self.formAyarlarGoster)
        self.btnAyarlar.setGeometry(QRect(self.width()-110,100,80,50))
        self.btnAyarlar.setStyleSheet("""QPushButton{color:white;}QPushButton:pressed 
                                        {background-color:blue(spread:pad, x1:0, y1:0, x2:0, y2:1,   
                                        stop:0 rgba(80, 175, 162, 255),  stop:1 rgba(98, 211, 162, 255))}QPushButton 
                                        {     background-color: rgb(61, 204, 199, 200); 
                                        border: 1px solid black;     border-radius: 5px;}""")
        self.btnAyarlar.setFont(QFont('Arial', 12))
        if os.path.exists("%s\\Ayarlar.json" % (os.getcwd())):
            with open("%s\\Ayarlar.json" % (os.getcwd()), 'r') as f:
                ayarlar = json.loads(f.read())
                self.YoneticiMail=ayarlar["Yonetici-Mail"]
                self.Karanlik=ayarlar["Karanlik"]
                if self.Karanlik:
                    self.setStyleSheet("QMainWindow{border-image:url(:/img/Iconlar/kapali.png) 0 0 0 0 stretch stretch}")
                    self.txtMailMesaj.setStyleSheet(
                        "background-color:rgba(255,255,255,25);color:white;border:1px solid cyan")
                    self.txtMailAdresi.setStyleSheet(
                        "background-color:rgba(255,255,255,25);color:white;border:1px solid cyan")
                    self.txtMailBaslik.setStyleSheet(
                        "background-color:rgba(255,255,255,25);color:white;border:1px solid cyan")
                else:
                    self.txtMailMesaj.setStyleSheet("background-color:rgba(255,255,255,25);color:white")
                    self.txtMailBaslik.setStyleSheet("background-color:rgba(255,255,255,100);color:white")
                    self.txtMailAdresi.setStyleSheet("background-color:rgba(255,255,255,100);color:white")
        self.txtMailMesaj.setFont(QFont('Arial',11))

        self.show()

    def formAyarlarGoster(self):
        try:
            self.formAyarlar= FormAyarlar(self)

        except Exception as err:
            print('formAyarlarGoster err: %s' % str(err))

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

    def Dogrula_VN(self, VN):
        valueVN = str(VN)
        if not len(valueVN) == 10:  # 10 haneli değilse
            return False

        if not valueVN.isdigit():  # rakamdan olusmuyorsa
            return False

        totalVN = 0  # toplam=0

        for x in xrange(0, 9):
            A = (int(valueVN[x]) + (9 - x)) % 10  # 1sayı ile 9 u 2.sayı ile 8i.... toplar %10=A
            B = (A * (2 ** (9 - x))) % 9  # 2^9'dan başlayarak 2 ye kadar olan sayılarla (B)*A %9 =C
            if A != 0 and B == 0:
                B = 9

            totalVN += B

        if totalVN % 10 == 0:
            check_num = 0
        else:
            check_num = 10 - (totalVN % 10)

        if int(valueVN[9]) == check_num:
            return True
        else:
            return False

    def Gonder(self):
        try:
            MailAdresi=self.txtMailAdresi.text()
            Mesaj = self.txtMailMesaj.text()  # Kullanicinin girecegi mesaji Mesaj degiskenine string olarak aliyoruz
            Baslik = self.txtMailBaslik.text()
            if (MailAdresi =="" or Mesaj=="" or Baslik==""):
                self.msgHata("Lütfen Mail Adresinin, Başlığın ve Mesaj kısmının dolu olduğuna emin olun.")
                return

            OLASI_tcno = re.findall("[1-9]{1}[0-9]{10}",Mesaj)
            OLASI_vergino = re.findall("[0-9]{10}", Mesaj)
            OLASI_kredino = re.findall("(?:5[1-5][0-9]{2}|222[1-9]|22[3-9][0-9]|2[3-6][0-9]{2}|27[01][0-9]|2720)[0-9]{12}", Mesaj)
            OLASI_dogumtarihi = re.findall("([1-9]|[12][0-9]|3[01])(\/?\.?\-?\s?)(0[1-9]|1[12])(\/?\.?\-?\s?)(19[0-9][0-9]|20[0][0-9]|20[1][0-8])", Mesaj)
            TCLER=[]
            TANE_TC= len(OLASI_kredino)
            TANE_VN = len(OLASI_vergino)
            TANE_KREDIKARTI= len(OLASI_kredino)
            TANE_DOGUMTARIHI=len(OLASI_dogumtarihi)
            for tc in OLASI_tcno:
                if self.Dogrula_TC(tc):
                    TCLER.append(tc)
                    TANE_TC+=1

            if TANE_TC == 0 and TANE_KREDIKARTI==0 and TANE_DOGUMTARIHI==0 and TANE_VN==0:
                if self.MailGonder(MailAdresi, Baslik, Mesaj, TCLER, OLASI_kredino, OLASI_dogumtarihi):
                    self.msgBasarili("Mail Başarıyla Gönderildi!")
                else:
                    self.msgHata("Mail Gönderilemedi!")
            else:
                gosterilecekMesaj="\t---- BİLGİLERİNİZ ----<br>"
                if TANE_TC > 0:
                    gosterilecekMesaj += "TC Kimlik: <font color='red'>%d</font><br>" % (TANE_TC)
                if TANE_VN > 0:
                    gosterilecekMesaj += "Vergi Numarası: <font color='red'>%d</font><br>" % (TANE_VN)
                if TANE_KREDIKARTI > 0:
                    gosterilecekMesaj += "Kredi Kartı: <font color='red'>%d</font><br>" % (TANE_KREDIKARTI)
                if TANE_DOGUMTARIHI > 0:
                    gosterilecekMesaj += "Doğum Tarihi: <font color='red'>%d</font><br>" % (TANE_DOGUMTARIHI)

                if self.msgYesNoUyariSoru("UYARI", gosterilecekMesaj+"<br>Adet Özel bilgileriniz bulunuyor.<br>Güvenliğiniz için özel bilgilerinizi göndermemenizi öneririz.<br><br>Yine de devam etmek istiyor musunuz?"):
                    if self.MailGonder(MailAdresi, Baslik, Mesaj, TCLER, OLASI_kredino, OLASI_dogumtarihi):
                        self.msgBasarili("Mail Başarıyla Gönderildi!")
                    else:
                        self.msgHata("Mail Gönderilemedi!")

            #print("%s - %s" % (str(OLASI_kredino), str(TCLER)))
        except Exception as err:
            print('Gonder Hata: %s' %str(err))
            self.debugHataPrint()


    def MailGonder(self, Adres, Baslik, Mesaj, TC, KREDIKARTI, DOGUMTARIHI):
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
            if self.YoneticiMail != "": # Yonetici Maili Ayarlardan girilmis ise
                context = ssl.create_default_context()
                SifreliMesaj = Mesaj
                for tc_ in TC:
                    SifreliMesaj = SifreliMesaj.replace(tc_,"*"*len(tc_))
                for kredikarti_ in KREDIKARTI:
                    SifreliMesaj = SifreliMesaj.replace(kredikarti_, "*" * len(kredikarti_))
                for dogumtarihi_ in DOGUMTARIHI:
                    if len(dogumtarihi_) == 5:
                        SifreliMesaj = SifreliMesaj.replace(dogumtarihi_[0]+dogumtarihi_[1]+dogumtarihi_[2]+dogumtarihi_[3]+dogumtarihi_[4],"*"*5) # [('24', ' ', '04', ' ', '2000')]

                msg = text(SifreliMesaj)
                msg['From'] = gonderici_Email
                msg['To'] = self.YoneticiMail
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

class FormAyarlar(QDialog):
    def __init__(self, parent):
        QDialog.__init__(self)
        self.parent= parent
        self.setWindowTitle("Ayarlar")
        self.setFixedSize(QSize(300,175))
        self.chkKaranlik = QCheckBox("Karanlık", self)
        self.chkKaranlik.stateChanged.connect(self.chkTikAtildi)
        self.txtYoneticiMail= QTextEdit(self)
        lblYonetici = QLabel('Yönetici Mail Adresi',self)
        self.btnKaydet=QPushButton("Kaydet", self)
        lblYonetici.setGeometry(QRect(10,10,self.width()-20, 25))
        self.txtYoneticiMail.setGeometry(QRect(10,45, self.width()-20, 32))
        self.txtYoneticiMail.setAlignment(Qt.AlignCenter)
        self.chkKaranlik.setGeometry(QRect(int((self.width()-60)/2),90,75,25))
        self.btnKaydet.setGeometry(QRect(10, 120, self.width()-20,35))
        self.setWindowIcon(QIcon(':/img/Iconlar/arama.png'))
        self.btnKaydet.clicked.connect(self.Kaydet)
        self.setWindowFlags(self.windowFlags() & ~Qt.WindowContextHelpButtonHint)


        if os.path.exists("%s\\Ayarlar.json" % (os.getcwd())):
            with open("%s\\Ayarlar.json" % (os.getcwd()), 'r') as f:
                ayarlar = json.loads(f.read())
                self.txtYoneticiMail.setText(ayarlar["Yonetici-Mail"])
                self.chkKaranlik.setChecked(ayarlar["Karanlik"])

        self.show()
    def chkTikAtildi(self, event):
        if event == 2: # 2 tik atildi, 0 tik kaldirildi
            self.parent.setStyleSheet("QMainWindow{border-image:url(:/img/Iconlar/kapali.png) 0 0 0 0 stretch stretch}")
            self.parent.txtMailMesaj.setStyleSheet("background-color:rgba(255,255,255,25);color:white;border:1px solid cyan")
            self.parent.txtMailAdresi.setStyleSheet("background-color:rgba(255,255,255,25);color:white;border:1px solid cyan")
            self.parent.txtMailBaslik.setStyleSheet("background-color:rgba(255,255,255,25);color:white;border:1px solid cyan")
        else:
            self.parent.setStyleSheet("QMainWindow{border-image:url(:/img/Iconlar/acik.png) 0 0 0 0 stretch stretch}")
            self.parent.txtMailMesaj.setStyleSheet("background-color:rgba(255,255,255,25);color:white;border:1px solid white")
            self.parent.txtMailAdresi.setStyleSheet("background-color:rgba(255,255,255,25);color:white;border:1px solid white")
            self.parent.txtMailBaslik.setStyleSheet("background-color:rgba(255,255,255,25);color:white;border:1px solid white")
    def Kaydet(self):
        try:
            json_data = {
                'Yonetici-Mail': self.txtYoneticiMail.toPlainText().strip(),
                'Karanlik': self.chkKaranlik.isChecked()
            }
            with open("%s\\Ayarlar.json" % (os.getcwd()), 'w') as outfile:
                json.dump(json_data, outfile)
            self.parent.Karanlik=self.chkKaranlik.isChecked()
            self.parent.YoneticiMail = self.txtYoneticiMail.toPlainText().strip()
            self.parent.msgBasarili("Ayarlar Başarıyla Kaydedildi!")
        except Exception as err:
            print('Kaydet err: %s' % str(err))

if __name__ == "__main__":
    app = QApplication(sys.argv)
    anapencere = MainWindow()
    desktop = QApplication.desktop()

    pencere_genislik = desktop.width()
    pencere_uzunluk = desktop.height()
    anapencere.move((pencere_genislik - anapencere.width()) / 2, (pencere_uzunluk - anapencere.height()) / 2)
    sys.exit(app.exec_())