import paramiko, re, os, time, gzip, zipfile
import pymysql.cursors
import pak.oracle_foris as ora #ubrat
from datetime import timedelta, datetime
from threading import Thread
from tkinter import Frame, Tk, Text, Scrollbar, BooleanVar, Checkbutton, Button, Entry, Label, messagebox
from cryptography.fernet import Fernet

# ставим по умолчанию маску текущей даты
date_mask = datetime.now().strftime("%Y%m%d_%H%M")[:-1] #
delta = '0'
mr = 'МРЮг'
search_word = 'Внесите сюда слово поиска'

mr_dict = {
	'МРЮг': {'hosts': ['xxx.xxx.xxx.xxx', 'xxx.xxx.xxx.xxx'], 'paths': ['/opt/smbb/logs', '/backup/logs/smbp'], 'link': 'patmaster' ,'port': 
		'passw',
		'new_paths': ['/opt/smbp/logs', '/backup/logs/smbp'],
		'new_hosts' : ['xxx.xxx.xxx.xxx', 'xxx.xxx.xxx.xxx','xxx.xxx.xxx.xxx','xxx.xxx.xxx.xxx','xxx.xxx.xxx.xxx','xxx.xxx.xxx.xxx','xxx.xxx.xxx.xxx'],
		'new_link': 'hp_mon_moscow', 'new_port': 'passw',
		'my_link': 'hpbsm', 'my_host': 'xxx.xxx.xxx.xxx', 'my_port': 'passw',
		'arch_host': 'xxx.xxx.xxx.xxx', 'arch_paths': ['path', 'path'],
		'link_arch': 'ppduser', 'port_arch': 'passw'}, 
	'МРМосква': {'hosts': ['xxx.xxx.xxx.xxx','xxx.xxx.xxx.xxx','xxx.xxx.xxx.xxx','xxx.xxx.xxx.xxx'], 'paths': ['/opt/smbp/logs', '/backup/logs/smbp'], 'link': 'hp_mon_moscow' ,'port':
		'passw',
		'new_paths': ['/opt/smbp/logs', '/backup/logs/smbp'],
		'new_hosts' : ['xxx.xxx.xxx.xxx','xxx.xxx.xxx.xxx','xxx.xxx.xxx.xxx','xxx.xxx.xxx.xxx','xxx.xxx.xxx.xxx','xxx.xxx.xxx.xxx','xxx.xxx.xxx.xxx','xxx.xxx.xxx.xxx','xxx.xxx.xxx.xxx'],
		'new_link': 'hp_mon_moscow', 'new_port': 'passw',
		'my_link': 'hpbsm', 'my_host': 'xxx.xxx.xxx.xxx', 'my_port': 'passw',
		'arch_host': 'xxx.xxx.xxx.xxx', 'arch_paths': ['path', 'path', 'path', 'path'],
		'link_arch': 'ppduser', 'port_arch': 'passw'},
	'МРСибирь': {'hosts': ['xxx.xxx.xxx.xxx', 'xxx.xxx.xxx.xxx'], 'paths': ['/opt/smbp/logs', '/backup/logs/smbp'], 'link': 'patmaster' ,'port': 
		'passw',
		'new_paths': ['/opt/smbp/logs', '/backup/logs/smbp'],
		'new_hosts' : ['xxx.xxx.xxx.xxx','xxx.xxx.xxx.xxx','xxx.xxx.xxx.xxx','xxx.xxx.xxx.xxx','xxx.xxx.xxx.xxx','xxx.xxx.xxx.xxx','xxx.xxx.xxx.xxx'],
		'new_link': 'patmaster', 'new_port': 'passw',
		'my_link': 'hpbsm', 'my_host': 'xxx.xxx.xxx.xxx', 'my_port': 'passw',
		'arch_host': 'xxx.xxx.xxx.xxx', 'arch_paths': ['path', 'path'],
		'link_arch': 'ppduser', 'port_arch': 'passw'}, 
	'МРСЗ': {'hosts': ['xxx.xxx.xxx.xxx', 'xxx.xxx.xxx.xxx'], 'paths': ['/opt/smbp/logs', '/backup/logs/smbp'], 'link': 'hpbsmnw' ,'port': 
		'passw',
		'new_paths': ['/opt/smbp/logs', '/backup/logs/smbp'],
		'new_hosts' : ['xxx.xxx.xxx.xxx','xxx.xxx.xxx.xxx','xxx.xxx.xxx.xxx','xxx.xxx.xxx.xxx','xxx.xxx.xxx.xxx','xxx.xxx.xxx.xxx','xxx.xxx.xxx.xxx'],
		'new_link': 'hp_mon_moscow', 'new_port': 'passw',
		'my_link': 'hpbsm', 'my_host': 'xxx.xxx.xxx.xxx', 'my_port': 'passw',
		'arch_host': 'xxx.xxx.xxx.xxx', 'arch_paths': ['path', 'path'],
		'link_arch': 'ppduser', 'port_arch': 'passw'}, 
	'МРПоволжье': {'hosts': ['xxx.xxx.xxx.xxx','xxx.xxx.xxx.xxx','xxx.xxx.xxx.xxx','xxx.xxx.xxx.xxx'], 'paths': ['/opt/smbb/logs', '/backup/logs/smbp'], 'link': 'hpbsm' ,'port': 
		'passw',
		'new_paths': ['/opt/smbp/logs', '/backup/logs/smbp'],
		'new_hosts' : ['xxx.xxx.xxx.xxx','xxx.xxx.xxx.xxx','xxx.xxx.xxx.xxx','xxx.xxx.xxx.xxx','xxx.xxx.xxx.xxx','xxx.xxx.xxx.xxx','xxx.xxx.xxx.xxx','xxx.xxx.xxx.xxx','xxx.xxx.xxx.xxx'],
		'new_link': 'hpbsm', 'new_port': 'passw',
		'my_link': 'hpbsm', 'my_host': 'xxx.xxx.xxx.xxx', 'my_port': 'passw',
		'arch_host': 'xxx.xxx.xxx.xxx', 'arch_paths': ['path', 'path', 'path', 'path'],
		'link_arch': 'ppduser', 'port_arch': 'passw'}
}

def sortByLength(inputStr):
    return len(inputStr)

def ungz(file_path):
    inF = gzip.GzipFile(file_path, 'rb')
    s = inF.read()
    inF.close()
    new_file_path = file_path[:-3]
    outF = open(new_file_path, 'wb')
    outF.write(s)
    outF.close()
    
def unzip(file_path):
    fantasy_zip = zipfile.ZipFile(file_path)
    fantasy_zip.extractall(os.path.dirname(file_path))
    fantasy_zip.close()	
	
class Assembly(Frame):
	def __init__(self, parent):
		Frame.__init__(self, parent, background="white")
		self.parent = parent
		self.parent.title("SMBP_logs")
		self.pack(fill='both', expand=True)
		
		panelFrame = Frame(self)
		textFrame = Frame(self)

		""" создаем фреймы верх-низ и далее в каждом фрейме создаем лево-право 
			или верх=низ фреймы, к которым будут привязаны объекты, чтобы
			в случае расширения формы нормально отображалось и перемещалось все
		"""
		panelFrame.pack(side='top', fill='both')
		textFrame.pack(side='bottom', fill='both', expand=True)

		panelFrameUp = Frame(panelFrame)
		panelFrameDown = Frame(panelFrame)
		
		panelFrameUp.pack(side='top', fill='both', expand=True)
		panelFrameDown.pack(side='bottom', fill='both', expand=True)
		
		panelFrameUpTop = Frame(panelFrameUp)
		panelFrameUpBottom = Frame(panelFrameUp)

		panelFrameUpTop.pack(side='top', fill='both', expand=True)
		panelFrameUpBottom.pack(side='bottom', fill='both', expand=True)
		
		panelFrameTop = Frame(panelFrameDown)
		panelFrameBottom = Frame(panelFrameDown, relief='raised', borderwidth=1)

		panelFrameTop.pack(side='top', fill='both', expand=True)
		panelFrameBottom.pack(side='bottom', fill='both', expand=True)

		textFrameLeft = Frame(textFrame)
		textFrameRight = Frame(textFrame)

		textFrameLeft.pack(side='left', fill='both', expand=True)
		textFrameRight.pack(side='right', fill='both', expand=True)

		textFrameRightTop = Frame(textFrameRight)
		textFrameRightBottom = Frame(textFrameRight)

		textFrameRightTop.pack(side='top', fill='both', expand=True)
		textFrameRightBottom.pack(side='bottom', fill='both', expand=True)

		# создаем экземпляры класса текстбокса передаем нужный фрейм
		self.txtBox_left = TxtBox(textFrameLeft)
		self.txtBox_rtop = TxtBox(textFrameRightTop)
		self.txtBox_rbottom = TxtBox(textFrameRightBottom)
		
		label_param = Label(panelFrameBottom, text="Параметры поиска. Маска: ")
		label_param.pack(side='left', padx=5, pady=5) 
		
		mask_entry = Entry(panelFrameBottom, width=15)
		mask_entry.pack(side='left', padx=5, pady=5)
		mask_entry.insert('end', date_mask)
		
		label_delta = Label(panelFrameBottom, text="Дельта в минутах: ")
		label_delta.pack(side='left', padx=5, pady=5) 

		def def_delta():
			if str(delta_btn['text']) == '0':
				delta_btn['text'] = '10'
			else:
				delta_btn['text'] = '0'		
		
		delta_btn = Button(panelFrameBottom, text=delta, width=3, command=def_delta)
		delta_btn.pack(side='left', padx=5, pady=5)
		
		# чекбокс проверки поиска по ТД
		self.check_on_td_var = BooleanVar()
		check_on_td = Checkbutton(panelFrameBottom, text='Поиск по TD', variable=self.check_on_td_var)
		self.check_on_td_var.set(True) 
		check_on_td.pack(side='left', padx=5, pady=5)

		btn_run = Button(panelFrameBottom, text='Поиск по файлам', width=15)#, command=pass)
		btn_run.pack(side='right', pady=1)
		
		btn_find_files = Button(panelFrameBottom, text='Поиск файлов', width=15)#, command=pass)
		btn_find_files.pack(side='right', padx=3, pady=1)

		# строка поиска
		label_find = Label(panelFrameTop, text="Строка поиска: ")
		label_find.pack(side='left', padx=5, pady=5) 
		
		find_entry = Entry(panelFrameTop)
		find_entry.pack(fill='x', padx=5, expand=True)
		find_entry.insert('end', search_word) 
		# если строка не изменялась при нажатии мышкой должна быть очищена
		def clean_find_entry(*args):
			if str(find_entry.get()) == search_word:
				find_entry.delete(0,'end')
		find_entry.bind('<Button-1>', clean_find_entry)
		
		# textbox 
		txt_mr = Text(panelFrameUpBottom, width=1, height=8)
		scrollbar_mr = Scrollbar(panelFrameUpBottom)
		scrollbar_mr['command'] = txt_mr.yview
		txt_mr['yscrollcommand'] = scrollbar_mr.set
		scrollbar_mr.pack(side ='right', fill='y')
		txt_mr.pack(fill='both', expand=True)
		
		# для передачи аргументов при нажатии кнопки поиска файлов
		btn_find_files.bind('<Button-1>', lambda _: find_files(txt_mr,
											self.txtBox_rbottom.txt_box,
											self.txtBox_rtop.txt_box,
											self.txtBox_left.txt_box,
											mask_entry, delta_btn))
											
		btn_run.bind('<Button-1>', lambda _: find_session(self.txtBox_rtop.txt_box, 
											self.txtBox_rbottom.txt_box, self.txtBox_left.txt_box,
											find_entry, mask_entry, self.check_on_td_var, btn_run))
	
		def select_mr(self, btn_mr):
			# все кнопки закрашиваем в цвет по умолчанию
			btn_mr1['bg'] = btn_mr2['bg'] = btn_mr3['bg'] = btn_mr4['bg'] = btn_mr5['bg'] = 'SystemButtonFace'
			# подкрашиваем только ту кнопку, что нажата
			btn_mr['bg'] = 'gray75'
			global mr
			# меняем регион с которым работаем
			mr =  btn_mr['text']
			# при смене мр меняем список серверов
			print_mr_list() #(btn_mr['text'])

		def	print_mr_list(*args):
			# очищаем текстбокс и выводим новый список серверов исходя из МР
			txt_mr.delete('1.0','end')
			# mr = args[0] 
			for host in mr_dict[mr]['hosts']:
				for path in mr_dict[mr]['paths']:
					txt_mr.insert('end', host + ' | ' + path + '\n')
			for host in mr_dict[mr]['new_hosts']:
				for path in mr_dict[mr]['new_paths']:
					txt_mr.insert('end', host + ' | ' + path + '\n')
			# если чекбокс стоит на архивных серверах - добавляем их 
			if self.check_arch_var.get():
				for path in mr_dict[mr]['arch_paths']:
					txt_mr.insert('end', str(mr_dict[mr]['arch_host']) + ' | ' + path + '\n')
			
		
		label_mr = Label(panelFrameUpTop, text="Выбор МР: ")
		label_mr.pack(side='left', padx=5, pady=5) 
		
		btn_mr1 = Button(panelFrameUpTop, text='МРЮг', width=10, bg = 'gray75')
		btn_mr1.pack(side='left', padx=1, pady=1) 
		# при нажатии кнопки вызываем процедуру перекраски мр
		btn_mr1.bind('<Button-1>', lambda _: select_mr(self,btn_mr1))
		
		btn_mr2 = Button(panelFrameUpTop, text='МРМосква', width=10)
		btn_mr2.pack(side='left', padx=1, pady=1)
		btn_mr2.bind('<Button-1>', lambda _: select_mr(self,btn_mr2))
		
		btn_mr3 = Button(panelFrameUpTop, text='МРСибирь', width=10)
		btn_mr3.pack(side='left', padx=1, pady=1)
		btn_mr3.bind('<Button-1>', lambda _: select_mr(self,btn_mr3))
		
		btn_mr4 = Button(panelFrameUpTop, text='МРСЗ', width=10)
		btn_mr4.pack(side='left', padx=1, pady=1)
		btn_mr4.bind('<Button-1>', lambda _: select_mr(self,btn_mr4))
		
		btn_mr5 = Button(panelFrameUpTop, text='МРПоволжье', width=10)
		btn_mr5.pack(side='left', padx=1, pady=1)
		btn_mr5.bind('<Button-1>', lambda _: select_mr(self,btn_mr5))

		self.check_arch_var = BooleanVar()
		check_arch = Checkbutton(panelFrameUpTop, text='Поиск по архивным серверам', variable=self.check_arch_var)
		self.check_arch_var.set(True)
		check_arch.pack(side='left', padx=5, pady=5)
		self.check_arch_var.trace('w', print_mr_list) 
		# один разок надо вызвать эту процедуру при инициализации
		select_mr(self,btn_mr1)

def find_session(txtBox_rtop, txtBox_rbottom, txtBox_left, find_entry, mask_entry, check_on_td_var, btn_run):
	"""Добавил возможность остановить поиск"""
	if btn_run['text'] == 'Остановить поиск':
		btn_run['text'] = 'Поиск по файлам'
	else:
		btn_run['text'] = 'Остановить поиск'
		search_word = folder_name = entity = str(find_entry.get().strip())
		txtBox_rtop.delete('1.0','end')
		txtBox_rbottom.delete('1.0','end')
		date_mask = str(mask_entry.get())
		if check_on_td_var.get():
			# в случае поиска по ТД нужно подключиться к MySQL и взять оттуда ТД исходя из msisdn
			connection_mysql = pymysql.connect(host=mr_dict[mr]['my_host'], user=mr_dict[mr]['my_link'], password=mr_dict[mr]['my_port'], charset='utf8mb4', cursorclass=pymysql.cursors.DictCursor)
			with connection_mysql.cursor() as cursor:
				sql_mysql = f"""
					SELECT epv1.value as value, epv1.entityId as entity
					FROM CUST.EntityPropertyValue epv1 
					WHERE epv1.entityPropertyKindId = 1
					and epv1.entityId = 
						(SELECT max(epv.entityId) 
						FROM CUST.EntityPropertyValue epv 
						WHERE epv.entityPropertyKindId = 3 
						AND epv.value = '{search_word}')
					limit 1"""
				cursor.execute(sql_mysql)
				TD = cursor.fetchall()

			if TD:
				old_search_word = search_word
				search_word = str(TD[0]['value'])
				entity = str(TD[0]['entity'])
				txtBox_rtop.insert('1.0',f'По {old_search_word} найден TD {search_word}\n', 'ok')
				#print('entity - !!!', entity)
			else:
				txtBox_rtop.insert('1.0',f'По {search_word} не найден TD\n', 'warn')
			connection_mysql.close()
		
		def call_paramiko_for_sessions(host, dict_host_files, finish_ad, btn_run):
			"""по каждому серверу в отдельном потоке соединяемся по SSH"""
			ssh = paramiko.SSHClient()
			ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
			# if host in mr_dict[mr]['hosts']:
				# ssh.connect(host, 22, mr_dict[mr]['link'], mr_dict[mr]['port'])
			# elif host in mr_dict[mr]['arch_host']:
				# ssh.connect(host, 22, mr_dict[mr]['link_arch'], mr_dict[mr]['port_arch'])
			# elif host in mr_dict[mr]['new_hosts']:
				# ssh.connect(host, 22, mr_dict[mr]['new_link'], mr_dict[mr]['new_port'])
			ssh.connect(host, 22, 'login', ora.serv_tt)
			
			sftp = ssh.open_sftp()
			sftp.sshclient = ssh
			
			dict_host_file_session = {}
			old_sessions = set()
			# идем по всем файлам, каждого сервака, отсортированным по дате
			for file in dict_host_files[host]:
				if btn_run['text'] == 'Остановить поиск':
					stdin, stdout, stderr = ssh.exec_command(fr'zgrep -w "{search_word}" {file}')
					txtBox_rbottom.insert('1.0', fr'{host} zgrep -w "{search_word}" {file}' + '\n')
					# получение множества(уникальных) сессий по первой цифре вначале строки
					stdout_read = ''
					stdout_read = stdout.read().decode().split('\n')
					sessions = {re.search(r'\d+', i).group(0) for i in stdout_read if i}
					if sessions:
						txtBox_rtop.insert('1.0',f'{host} {sessions} {file}\n')
						txtBox_rbottom.insert('1.0',f'{host} {sessions} {file} найдено {stdout_read[0]}\n', 'grey_txt')
						# в случае нахождения сессии в файле записываем в отдельный словарь по каждому файлу
						dict_host_file_session[host] = {file: sessions}
						# по каждой сессии, найденной в файле нужно искать данные в остальных файлах ниже по списку файлов
						for session in sessions:
							if (session not in old_sessions) and (btn_run['text'] == 'Остановить поиск'):
								old_sessions.add(session)
								cnt_files_session = 15
								for s_file in dict_host_files[host]:
									if cnt_files_session and (btn_run['text'] == 'Остановить поиск'):
										# начинаем поиск в файлах по списку индекс которого больше, чем файла, где была найдена сессия
										if dict_host_files[host].index(s_file) >= dict_host_files[host].index(file):
											log_name = f'{date_mask}_{session}_{host}.log'
											cnt_files_session -= 1
											
											stdin, stdout, stderr = ssh.exec_command(fr'zgrep {session} {s_file} >> /tmp/{log_name}')
											txtBox_rbottom.insert('1.0', fr'{host} zgrep {session} {s_file} >> /tmp/{log_name}' +'\n', 'non_ok')
											# ожидаем окончание выполнения команды
											stdout.channel.recv_exit_status()
											
									else:
										break
								
								
								# ищем внутри файла с логами только то, что касается нашего абона. ищем сессии
								stdin, stdout, stderr = ssh.exec_command(fr'zegrep -w "{search_word}|{folder_name}|{entity}" /tmp/{log_name}')
								txtBox_rbottom.insert('1.0', fr'zegrep -w "{search_word}|{folder_name}|{entity}" /tmp/{log_name}' +'\n')
								# находим сессии - то что внутри фигурных скобок. раскидываем на номера в списке
								max_ses = [re.search(r'{\d+\S*}', i).group(0).strip('{}').split('#') for i in stdout.read().decode().split('\n') if i]
								max_ses.sort(key=sortByLength, reverse=True)
								stdout.channel.recv_exit_status()
								# найдена самая длинная сессия. нужно взять не ее, а копию - list
								sum_ses = list(max_ses[0])
								
								# нам нужны только уникальные сессии ставим множества
								for i in range(len(sum_ses)):
									sum_ses[i] = {sum_ses[i]}

								# наполняем на каждый уровень дочерности уникальными номерами сессии
								for ses in max_ses:
									for i,j in enumerate(ses):
										sum_ses[i].add(j)
								# тут нам нужна только первая сессия из множества
								small_sessions = [[] for i in sum_ses]
								small_sessions[0] = [i for i in sum_ses[0] if i]
								for i, ses in enumerate(sum_ses):
									for j in sum_ses[i]:
										# собираем все сессии с учетом предыдущего уровня
										small_sessions[i] += [str(a + '#' + j) for a in small_sessions[i-1]]

								# перебираем сессии, что у нас есть по всем уровням по порядочку
								for list_small_session in small_sessions:
									for small_session in list_small_session:
										small_session = '{' + small_session + '}'
										#print(small_session)
										stdin, stdout, stderr = ssh.exec_command(fr'zgrep "{small_session}" /tmp/{log_name} >> /tmp/small_{log_name}')
										txtBox_rbottom.insert('1.0', fr'zgrep "{small_session}" /tmp/{log_name} >> /tmp/small_{log_name}' +'\n')
										stdout.channel.recv_exit_status()
								
								# найдем typeid
								typeid = ''
								try:
									stdin, stdout, stderr = ssh.exec_command(fr'zgrep -m1 "01: eventTypeId=" /tmp/small_{log_name}')
									typeid = stdout.read().decode().split('01: eventTypeId=')[1].strip('\n')
									stdout.channel.recv_exit_status()
								except IndexError:
									typeid = 'None'
								
								# сжимаем файл, в который сливались данные и в конце появляется gz
								stdin, stdout, stderr = ssh.exec_command(fr'gzip /tmp/small_{log_name}')
								stdout.channel.recv_exit_status()
								stdin, stdout, stderr = ssh.exec_command(fr'gzip /tmp/{log_name}')
								txtBox_rbottom.insert('1.0', fr'{host} gzip /tmp/{log_name}' + '\n')
								# создаем папку с названием запроса, если ее нет
								if not os.path.exists(os.getcwd() + fr'\pyscripts\output\{folder_name}'):
									os.makedirs(os.getcwd() + fr'\pyscripts\output\{folder_name}')
								# ожидаем окончание выполнения команды
								stdout.channel.recv_exit_status()

								# переносим файл из линукса в винду и накинем typeid
								sftp.get(fr'/tmp/small_{log_name}.gz', os.getcwd() + fr'\pyscripts\output\{folder_name}\small_{typeid}_{log_name}.gz')
								sftp.get(fr'/tmp/{log_name}.gz', os.getcwd() + fr'\pyscripts\output\{folder_name}\{typeid}_{log_name}.gz')
								# удаляем файл из /tmp/ 
								stdin, stdout, stderr = ssh.exec_command(fr'rm /tmp/small_{log_name}.gz')
								# txtBox_rbottom.insert('1.0', f'Лог "small_{log_name}.gz" выгружен в output \n', 'ok')
								stdin, stdout, stderr = ssh.exec_command(fr'rm /tmp/{log_name}.gz')
								txtBox_rbottom.insert('1.0', f'Лог "{typeid}_{log_name}.gz" выгружен в output \n', 'ok')
			txtBox_rtop.insert('1.0', f'Поиск по серверу {host} завершен. \n')
			sftp.close()
			ssh.close()
			finish_ad[host] = 1
			if is_finished(finish_ad):
				btn_run['text'] = 'Поиск по файлам'
				txtBox_rtop.insert('1.0', f'Поиск по всем серверам завершен по запросу {search_word}.\n', 'non_ok')
				if re.search(r'{', str(txtBox_rtop.get("1.0", "end-1c"))):	
					messagebox.showinfo('Поиск завершен', 'логи нужно искать тут: \n ' + os.getcwd() + fr'\pyscripts\output\{folder_name}')
					# разархивировать все файлы в папке у кого есть gz и удалить сам архив каждый
					# заархивировать все файлы смол в один и все файлы без смол в другой
					zip_path = os.getcwd() + fr'\pyscripts\output\{folder_name}'
					# получаем список файлов в директории , куда выгрузили архивы
					files = os.listdir(zip_path)
					for file in files:
						if file[-3:] == '.gz':
							ungz(os.path.join(zip_path, file))
							os.remove(os.path.join(zip_path, file))
						if file[-3:] == 'zip':
							unzip(os.path.join(zip_path, file))
							os.remove(os.path.join(zip_path, file))

					files =  os.listdir(zip_path)
					small_zip = zipfile.ZipFile(os.path.join(zip_path,f'small_{folder_name}.zip'), 'w')
					else_zip = zipfile.ZipFile(os.path.join(zip_path,f'{folder_name}.zip'), 'w')

					for file in files:
						if file[:5] == 'small':
							small_zip.write( os.path.join(zip_path, file) , file, compress_type=zipfile.ZIP_DEFLATED)
						else:
							else_zip.write( os.path.join(zip_path, file) , file, compress_type=zipfile.ZIP_DEFLATED)
						os.remove(os.path.join(zip_path, file))
					else_zip.close() 
					small_zip.close() 					
				else:
					messagebox.showinfo('Поиск завершен', 'Логи не удалось найти. попробуйте изменить маску даты')
					
		
		dict_host_files = {}
		# словарь с хостом и списком файлов наполняем из текстбокса в виде СПИСКА:
		for row in txtBox_left.get("1.0", "end-1c").split('\n'):
			if row:
				if row.split()[0] in dict_host_files:
					dict_host_files[row.split()[0]].append(row.split()[1])
				else:
					dict_host_files[row.split()[0]] = [row.split()[1]]	
		
		# запускаем потоки на каждый сервер
		finish_ad = {host: 0 for host in dict_host_files}
		for host in dict_host_files:
			my_thread = Thread(target=call_paramiko_for_sessions, args=(host, dict_host_files, finish_ad, btn_run))
			my_thread.start()

def find_files(txt_mr, txtBox_rbottom, txtBox_rtop, txtBox_left, mask_entry, delta_btn):
	txtBox_left.delete('1.0','end')
	txtBox_rtop.delete('1.0','end')
	# считываем списки сервер - каталог логов, по которому будем итерироваться
	list_paths = [[j.strip() for j in i.split('|')] for i in txt_mr.get("1.0", "end-1c").split('\n') if i]
	def call_paramiko_for_files(list_path, finish_ad):
		ssh = paramiko.SSHClient()
		ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
		host = list_path[0]
		
		date_mask = str(mask_entry.get().strip())
		# доступ отличается на сервера, где хранятся архивные логи
		# if host in mr_dict[mr]['hosts']:
			# ssh.connect(host, 22, mr_dict[mr]['link'], mr_dict[mr]['port'])
		# elif host in mr_dict[mr]['arch_host']:
			# ssh.connect(host, 22, mr_dict[mr]['link_arch'], mr_dict[mr]['port_arch'])
		# elif host in mr_dict[mr]['new_hosts']:
			# ssh.connect(host, 22, mr_dict[mr]['new_link'], mr_dict[mr]['new_port'])
		ssh.connect(host, 22, 'login', ora.serv_tt)
		# главная команда - получаем имена файлов, что нам нужны по маске
		stdin, stdout, stderr = ssh.exec_command(fr'find {list_path[1]} -name "*{date_mask}*"')

		# получаем список файлов из ответа stdout
		files = {i for i in stdout.read().decode().split('\n') if i}
		txtBox_rbottom.insert('end', fr'find {list_path[1]} -name "*{date_mask}*"' + '\n')
		# выводим в текстбокс ошибку выполнения команды, если она есть
		stderr_read = stderr.read().decode().strip('\n')
		if stderr_read:
			txtBox_rbottom.insert('end',host + ': ' + stderr_read + '\n')
		
		# если включено использование дельты +-10 минут, ищем файлы вокруг даты по маске
		if delta_btn['text'] != '0':
			temp_date_mask = date_mask
			if len(temp_date_mask) < 15:
				for _ in range(15 - len(temp_date_mask)):
					temp_date_mask += '0'
			date_mask_dp = (datetime.strptime(temp_date_mask, "%Y%m%d_%H%M%S")+
							timedelta(minutes=int(delta_btn['text']))).strftime("%Y%m%d_%H%M")[:-1]
			stdin_dp, stdout_dp, stderr_dp = ssh.exec_command(fr'find {list_path[1]} -name "*{date_mask_dp}*"')
			date_mask_dm = (datetime.strptime(temp_date_mask, "%Y%m%d_%H%M%S")-
							timedelta(minutes=int(delta_btn['text']))).strftime("%Y%m%d_%H%M")[:-1]
			stdin_dm, stdout_dm, stderr_dm = ssh.exec_command(fr'find {list_path[1]} -name "*{date_mask_dm}*"')
			files_delta_plus = {i for i in stdout_dp.read().decode().split('\n') if i}
			files_delta_minus = {i for i in stdout_dm.read().decode().split('\n') if i}
			# объединяем множетства
			files = files|files_delta_plus|files_delta_minus
		
		ssh.close()
		
		# добавляем найденные файлы в текстбокс
		if files:
			for file in files:
				txtBox_left.insert('1.0', host + ' ' + file + '\n')	
		
		# выводим количество найденных файлов
		txtBox_rtop.insert('1.0', f'поиск по {list_path} - {len(files)}шт\n')
		# указывем в словаре окончания работ, что по данному сервер-путь_логов завершено
		finish_ad[tuple(list_path)] = 1

		if is_finished(finish_ad):
			# в случае одноверменного завершения возможно задубливание, поэтому:
			finish_ad[tuple(list_path)] = 0
			# вносим данные из текстбокса в словарь - (дата,хост): список хост-файл
			# чтобы отсортировать по дате , затем вывести в текстбокс все данные
			dict_txtbox_rows = {(datetime.strptime(i.split('smbp_')[1].split('.')[0], "%Y%m%d_%H%M%S"), i): 
						[i.split()[0], i.split()[1]] for i in txtBox_left.get("1.0", "end-1c").split('\n') if i}
			txtBox_left.delete('1.0','end')
			list_txtbox_rows = list(dict_txtbox_rows.keys())
			# сортируем список дат
			list_txtbox_rows.sort()
			for row in list_txtbox_rows:
				txtBox_left.insert('end', dict_txtbox_rows[row][0] + ' ' + dict_txtbox_rows[row][1] + '\n')
			txtBox_rtop.insert('1.0', f'Поиск по маске {date_mask} завершен. Найдено всего {len(list_txtbox_rows)} файлов\n')
		
	# создаем словарь сервер-путь_логов тапл: 0 , чтобы потом отследить окончание работ
	finish_ad = {tuple(list_path): 0 for list_path in list_paths}
	for list_path in list_paths:
		my_thread = Thread(target=call_paramiko_for_files, args=(list_path, finish_ad))
		my_thread.start()

def is_finished(check):
	t = 0
	for i in check:
		t += check[i]
	if t == len(check):
		return True
	else:
		return False
		
# Класс для создания исключительно текстбоксов с нужными свойствами
class TxtBox():

	def __init__(self, txt_frame):
		self.txt_frame = txt_frame
		self.txt_box = Text(self.txt_frame, font='Tahoma 11', wrap='word', width=1, height=1)
		self.scrollbar = Scrollbar(self.txt_frame)
		self.scrollbar['command'] = self.txt_box.yview
		self.txt_box['yscrollcommand'] = self.scrollbar.set
		self.txt_box.pack(side='left', fill='both', expand=True)
		self.scrollbar.pack(side='right', fill='y')
		self.txt_box.tag_config('grey_txt', background='gray85')
		self.txt_box.tag_config('ok',background='pale green')
		self.txt_box.tag_config('warn',background='tomato')
		self.txt_box.tag_config('non_ok',background='peach puff')

def main():
	root = Tk()
	root.geometry("1200x700+300+100")
	Assembly(root)
	root.mainloop()

if __name__ == '__main__':
	main()
