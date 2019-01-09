import paramiko
from datetime import timedelta, datetime
import zipfile, json
import pak.oracle_foris as ora
import matplotlib.pyplot as plt
import matplotlib.dates as mdates
import datetime as dt
import pandas as pd
import smtplib, email, os
from email.mime.multipart import MIMEMultipart
from email.mime.base import MIMEBase
from email.mime.text import MIMEText
from tkinter import Tk, Text, TOP, BOTH, END, X, N, LEFT, Frame, Label, Entry, Button, Listbox

mr_dict = ora.mr_dict

def check_date_mask(date_mask, mr):
	if mr == 'МРСибирь':
		leap = timedelta(hours=4)
	else:
		leap = timedelta(hours=0)
	try:
		enter_date = datetime.strptime(date_mask,"%Y%m%d_%H")
	except ValueError:
		print('Некорретная дата - ставлю наибольшую')
		return (datetime.now() - timedelta(hours=26) + leap).strftime("%Y%m%d_%H")
	if enter_date < datetime(2018, 2, 16):
		enter_date = datetime(2018, 2, 16)
	if enter_date > (datetime.now() - timedelta(hours=26) + leap):
		enter_date = (datetime.now() - timedelta(hours=26) + leap)
	return enter_date.strftime("%Y%m%d_%H")

def prnt_plot2(df, host1, host2):
	fig = plt.figure(figsize=(14, 7))

	ax1 = fig.add_subplot(311)
	ax11 = ax1.twinx()
	ax2 = fig.add_subplot(312)
	plt.ylabel('Количество событий в час')
	ax22 = ax2.twinx()
	plt.ylabel('Количество ошибок в час - красным пунктиром')
	ax3 = fig.add_subplot(313)

	ax11.plot(df[0]['Date'], df[0]['error_sum'],'r:', label = 'error_sum' )
	ax22.plot(df[1]['Date'], df[1]['error_sum'],'r:', label = 'error_sum' )

	ax3.plot(df[0]['Date'], df[0]['file_size'], 'o-', label=f'Files_size {host1}')
	ax3.plot(df[1]['Date'], df[1]['file_size'], 'o-', label=f'Files_size {host2}')

	for reg in df[0].columns:
		if reg != 'Files_size' and reg != 'Date' and reg != 'error' and reg != 'error_sum' and df[0][reg].sum() > 10000:
			ax1.plot(df[0]['Date'], df[0][reg], 'o-', label=reg)
	for reg in df[1].columns:
		if reg != 'Files_size' and reg != 'Date' and reg != 'error' and reg != 'error_sum' and df[1][reg].sum() > 10000:
			ax2.plot(df[1]['Date'], df[1][reg], 'o-', label=reg)
			

	ax3.xaxis.set_major_locator(mdates.HourLocator())
	ax3.xaxis.set_major_formatter(mdates.DateFormatter('%m.%d-%H'))

	for label in ax3.xaxis.get_ticklabels():
		label.set_rotation(40)
		label.set_fontsize(8)

	ax1.yaxis.grid(True, color='grey', linestyle='dashed', alpha=0.5)
	ax1.xaxis.grid(True, color='grey', linestyle='dashed', alpha=0.5)
	ax2.yaxis.grid(True, color='grey', linestyle='dashed', alpha=0.5)
	ax2.xaxis.grid(True, color='grey', linestyle='dashed', alpha=0.5)
	ax3.yaxis.grid(True, color='grey', linestyle='dashed', alpha=0.5)
	ax3.xaxis.grid(True, color='grey', linestyle='dashed', alpha=0.5)

	ax1.legend(loc='best')
	ax2.legend(loc='best')
	ax3.legend(loc='best')

	plt.xlabel('Формат даты месяц.день - час')
	plt.ylabel('объем логов ГБ/час')

	fig.savefig(os.getcwd() + '/new_events.png')

	plt.clf()
	
	df11 = pd.DataFrame([i if i!=0 else {} for i in df[0]['error']])
	df11.fillna(0,inplace=True)
	df111 = pd.concat([df[0][['Date','error_sum']], df11], axis=1)
	df111.to_csv(os.getcwd() + f'/error1_{host1}.csv', sep=';')

	df22 = pd.DataFrame([i if i!=0 else {} for i in df[1]['error']])
	df22.fillna(0,inplace=True)
	df222 = pd.concat([df[1][['Date','error_sum']], df22], axis=1)
	df222.to_csv(os.getcwd() + f'/error2_{host2}.csv', sep=';')

	fantasy_zip = zipfile.ZipFile(os.getcwd() + '/errors_s.zip', 'w')
	 
	fantasy_zip.write(os.getcwd() + f'/error1_{host1}.csv', f'/error1_{host1}.csv', compress_type=zipfile.ZIP_DEFLATED)
	fantasy_zip.write(os.getcwd() + f'/error2_{host2}.csv', f'/error2_{host2}.csv', compress_type=zipfile.ZIP_DEFLATED)

	fantasy_zip.close()

def prnt_plot4(df, host1, host2, host3, host4):
	fig = plt.figure(figsize=(14, 12))

	ax1 = fig.add_subplot(511)
	ax11 = ax1.twinx()
	ax2 = fig.add_subplot(512)
	ax22 = ax2.twinx()
	ax3 = fig.add_subplot(513)
	plt.ylabel('Количество событий в час')
	ax33 = ax3.twinx()
	plt.ylabel('Количество ошибок в час - красным пунктиром')
	ax4 = fig.add_subplot(514)
	ax44 = ax4.twinx()
	ax5 = fig.add_subplot(515)

	ax11.plot(df[0]['Date'], df[0]['error_sum'],'r:', label = 'error_sum' )
	ax22.plot(df[1]['Date'], df[1]['error_sum'],'r:', label = 'error_sum' )
	ax33.plot(df[2]['Date'], df[2]['error_sum'],'r:', label = 'error_sum' )
	ax44.plot(df[3]['Date'], df[3]['error_sum'],'r:', label = 'error_sum' )

	ax5.plot(df[0]['Date'], df[0]['file_size'], 'o-', label=f'Files_size {host1}')
	ax5.plot(df[1]['Date'], df[1]['file_size'], 'o-', label=f'Files_size {host2}')
	ax5.plot(df[2]['Date'], df[2]['file_size'], 'o-', label=f'Files_size {host3}')
	ax5.plot(df[3]['Date'], df[3]['file_size'], 'o-', label=f'Files_size {host4}')

	for reg in df[0].columns:
		if reg != 'Files_size' and reg != 'Date' and reg != 'error' and reg != 'error_sum' and df[0][reg].sum() > 10000:
			ax1.plot(df[0]['Date'], df[0][reg], 'o-', label=reg)
	for reg in df[1].columns:
		if reg != 'Files_size' and reg != 'Date' and reg != 'error' and reg != 'error_sum' and df[1][reg].sum() > 10000:
			ax2.plot(df[1]['Date'], df[1][reg], 'o-', label=reg)
	for reg in df[2].columns:
		if reg != 'Files_size' and reg != 'Date' and reg != 'error' and reg != 'error_sum' and df[2][reg].sum() > 10000:
			ax3.plot(df[2]['Date'], df[2][reg], 'o-', label=reg)
	for reg in df[3].columns:
		if reg != 'Files_size' and reg != 'Date' and reg != 'error' and reg != 'error_sum' and df[3][reg].sum() > 10000:
			ax4.plot(df[3]['Date'], df[3][reg], 'o-', label=reg)


	ax5.xaxis.set_major_locator(mdates.HourLocator())
	ax5.xaxis.set_major_formatter(mdates.DateFormatter('%m.%d-%H'))

	for label in ax5.xaxis.get_ticklabels():
		label.set_rotation(40)
		label.set_fontsize(8)

	ax1.yaxis.grid(True, color='grey', linestyle='dashed', alpha=0.5)
	ax1.xaxis.grid(True, color='grey', linestyle='dashed', alpha=0.5)
	ax2.yaxis.grid(True, color='grey', linestyle='dashed', alpha=0.5)
	ax2.xaxis.grid(True, color='grey', linestyle='dashed', alpha=0.5)
	ax3.yaxis.grid(True, color='grey', linestyle='dashed', alpha=0.5)
	ax3.xaxis.grid(True, color='grey', linestyle='dashed', alpha=0.5)
	ax4.yaxis.grid(True, color='grey', linestyle='dashed', alpha=0.5)
	ax4.xaxis.grid(True, color='grey', linestyle='dashed', alpha=0.5)
	ax5.yaxis.grid(True, color='grey', linestyle='dashed', alpha=0.5)
	ax5.xaxis.grid(True, color='grey', linestyle='dashed', alpha=0.5)

	ax1.legend(loc='best')
	ax2.legend(loc='best')
	ax3.legend(loc='best')
	ax4.legend(loc='best')
	ax5.legend(loc='best')

	plt.xlabel('Формат даты месяц.день - час')
	plt.ylabel('объем логов ГБ/час')

	fig.savefig(os.getcwd() + '/new_events.png')

	plt.clf()
	
	df11 = pd.DataFrame([i if i!=0 else {} for i in df[0]['error']])
	df11.fillna(0,inplace=True)
	df111 = pd.concat([df[0][['Date','error_sum']], df11], axis=1)
	df111.to_csv(os.getcwd() + f'/error1_{host1}.csv', sep=';')

	df22 = pd.DataFrame([i if i!=0 else {} for i in df[1]['error']])
	df22.fillna(0,inplace=True)
	df222 = pd.concat([df[1][['Date','error_sum']], df22], axis=1)
	df222.to_csv(os.getcwd() + f'/error2_{host2}.csv', sep=';')

	df33 = pd.DataFrame([i if i!=0 else {} for i in df[2]['error']])
	df33.fillna(0,inplace=True)
	df333 = pd.concat([df[2][['Date','error_sum']], df33], axis=1)
	df333.to_csv(os.getcwd() + f'/error3_{host3}.csv', sep=';')

	df44 = pd.DataFrame([i if i!=0 else {} for i in df[3]['error']])
	df44.fillna(0,inplace=True)
	df444 = pd.concat([df[3][['Date','error_sum']], df44], axis=1)
	df444.to_csv(os.getcwd() + f'/error4_{host4}.csv', sep=';')

	fantasy_zip = zipfile.ZipFile(os.getcwd() + '/errors_s.zip', 'w')
	 
	fantasy_zip.write(os.getcwd() + f'/error1_{host1}.csv', f'/error1_{host1}.csv', compress_type=zipfile.ZIP_DEFLATED)
	fantasy_zip.write(os.getcwd() + f'/error2_{host2}.csv', f'/error2_{host2}.csv', compress_type=zipfile.ZIP_DEFLATED)
	fantasy_zip.write(os.getcwd() + f'/error3_{host3}.csv', f'/error3_{host3}.csv', compress_type=zipfile.ZIP_DEFLATED)
	fantasy_zip.write(os.getcwd() + f'/error4_{host4}.csv', f'/error4_{host4}.csv', compress_type=zipfile.ZIP_DEFLATED)
	fantasy_zip.close()
	
def send_mail(sender, destination_to, destination_cc, subject, text_message, files, mr):
	msg = MIMEMultipart()
	msg['From'] = sender
	msg['To'] = ', '.join(destination_to)
	msg['cc'] = ', '.join(destination_cc)
	msg['Subject'] = subject

	msg_html = MIMEText((text_message).encode('utf-8'), 'html', 'utf-8')
	msg.attach(msg_html)

	for filename in files:
		if(os.path.exists(filename) and os.path.isfile(filename)):
			filename = os.path.basename(filename)
			with open(filename, 'rb') as file:
				ctype = 'application/octet-stream'
				maintype, subtype = ctype.split('/', 1)
			
				msg_attach = MIMEBase(maintype, subtype)
				msg_attach.set_payload(file.read())
				email.encoders.encode_base64(msg_attach)
				msg_attach.add_header('Content-Disposition', 'attachment', filename=filename)
				msg.attach(msg_attach)
				file.close()
		else:
			print('Файл для атача не найден: ' + filename)

	try:
		smtp_obj = smtplib.SMTP('mail.spb.mts.ru', 25)
		smtp_obj.set_debuglevel(0)
		smtp_obj.ehlo()
		smtp_obj.starttls()
		smtp_obj.ehlo()
		smtp_obj.login(msg['From'], mr_dict[mr]['SSH2'])
		smtp_obj.sendmail(msg['From'], destination_to + destination_cc, msg.as_string())
	except smtplib.SMTPException as err:
		print('Ошибка при отправке e-mail сообщения: ', err)
	finally:
		smtp_obj.quit()
		


class Otchet:
	def __init__(self, hosts, user, SSH2, date_mask):
		self.user = user
		self.SSH2 = SSH2
		df = []
		for host in hosts:
			df.append(self.get_ssh_data(date_mask, host))
		if len(df) == 2:
			prnt_plot2(df, hosts[0], hosts[1])
		elif len(df) == 4:
			prnt_plot4(df, hosts[0], hosts[1], hosts[2], hosts[3])

		
	def get_ssh_data(self, date_mask, host):
		client = paramiko.SSHClient()
		client.set_missing_host_key_policy(paramiko.AutoAddPolicy())
		client.connect(hostname=host, username=self.user, password=self.SSH2, port=22)
		stdin, stdout, stderr = client.exec_command(r"zgrep -B24 -A24 '{}' /backup/logs/count_events_s_hour.csv".format(date_mask))
		df = pd.DataFrame([json.loads(i) for i in stdout.read().decode("utf-8").split('\n') if i])
		client.close()
		df.fillna(0,inplace=True)
		
		for i in range(len(df)):
			df.loc[i,'Date'] = dt.datetime.strptime(df.loc[i,'Date'], "%Y%m%d_%H")
			df.loc[i,'file_size'] = df.loc[i,'file_size'] / (1024 * 1024 * 1024)
			
		df['error_sum'] = 0
		for row_id in range(len(df)):
			if df.loc[row_id,'error']:
				for key,value in df.loc[row_id,'error'].items():
					df.loc[row_id,'error_sum'] += value
		return df

class OtchetForm(Frame):
	def __init__(self, parent):
		Frame.__init__(self, parent)   
		self.parent = parent
		self.initUI()
		
	def initUI(self):
		self.parent.title("p s logs Report")
		self.pack(fill=BOTH, expand=True)
		
		def run_send():
			selection = mr_listbox.curselection()
			if not selection:
				print('не выбран МР - выберем МРСЗ')
				mr = 'МРСЗ'
			else:
				mr = mr_listbox.get(selection[0]).strip()
			e_mail = entry1.get().strip()
			date_mask = entry2.get().strip()
			print(e_mail, date_mask, mr)
			send(e_mail, date_mask, mr)
			
		def erase(event):
			entry1.delete(0,'end')
		
		frame1 = Frame(self)
		frame1.pack(fill=X)
		
		lbl1 = Label(frame1, text="email to", width=8)
		lbl1.pack(side=LEFT, padx=5, pady=5)
	   
		entry1 = Entry(frame1)
		entry1.pack(fill=X, padx=5, expand=True)
		entry1.insert(END, 'palevch2@mts.ru')
		entry1.bind('<Button-1>',erase)

		frame2 = Frame(self)
		frame2.pack(fill=X)
		
		lbl2 = Label(frame2, text="Date mask", width=8)
		lbl2.pack(side=LEFT, padx=5, pady=5)
 
		entry2 = Entry(frame2)
		entry2.pack(fill=X, padx=5, expand=True)
		entry2.insert(END, (datetime.now() - timedelta(hours=26)).strftime("%Y%m%d_%H"))
		
		frame3 = Frame(self)
		frame3.pack(fill=BOTH, expand=True)
		
		run_send_button = Button(frame3, text="SEND", command=run_send, width=7)
		run_send_button.pack(side=LEFT, anchor=N, padx=5, pady=5)
		
		mr_listbox = Listbox(frame3)
		mr_listbox.pack(fill=BOTH, pady=5, padx=5, expand=True)
		
		for mr_name in mr_dict:
			mr_listbox.insert(END," " + mr_name)

def main():
	root = Tk()
	root.geometry("300x175+400+400")
	app = OtchetForm(root)
	root.mainloop()
			
def send(e_mail, date_mask, mr):
	date_mask = check_date_mask(date_mask, mr)
	t = Otchet(**mr_dict[mr], date_mask=date_mask)
			
	subject = f'Отчет по логам за два дня по {mr}'
	html = """<h4>Количество событий в {} по запросу: маска даты {} </h4>
		<IMG border=0 src="new_events.png" useMap=#FPMap0><p>8204	SwitchServiceIfNeed_v02</p>
		<p>8205	RegisterTarifficationOfSwitchServices_v02</p><p>8206	GetEntityProperties</p>
		<p>8207	GetActivationDates_v02</p><p>8209	blockUnblockCustomer</p><p>2050	GetSwitchableServiceInfoByMSISDN </p>
		<p>10267	GetSwitchableServiceInfoByMSISDN2</p>""".format(mr, date_mask)

	send_mail( 'login@inpochta.ru', # отправитель
	[e_mail], # получатель
	[], # в копию
	subject, # тема сообщения 
	html, # текст письма
	[os.getcwd() + '/new_events.png', os.getcwd() + '/errors_s.zip'],
	mr
	)

if __name__ == '__main__':
	main()
