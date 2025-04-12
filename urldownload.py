#
#	@utor Izaqux
#	Python
#

#	Url download, se tem arquivo na url, para baixar, então os arquivos, vai ser baixados tem modo de ver se tem arquivos

import os
import sys
import requests
from bs4 import BeautifulSoup
from urllib.parse import urljoin, urlparse, unquote
from textwrap import wrap
import argparse
import tempfile

# Config de exibição
MAXLINEWIDTH = 70
FILELISTWIDTH = 60

def pHeader(title):
	print("\n" + "=" * MAXLINEWIDTH)
	print(f" {title} ".center(MAXLINEWIDTH, " "))
	print("=" * MAXLINEWIDTH)

def pFooter():
	print("=" * MAXLINEWIDTH)

def decodeUrlFileName(url):
	decodeUrl = unquote(url)
	replacements = {
	"%20": ' ',
	"%C3%A1": 'á',
	"%C3%A9": 'é',
	"%C3%AD": 'í',
	"%C3%B3": 'ó',
	"%C3%BA": 'ú',
	"%C3%A3": 'ã',
	"%C3%A2": 'â',
	"%C3%AA": 'ê',
	"%C3%B5": 'õ',
	"%C3%A7": 'ç'
	}
	fileName = decodeUrl.split('/')[-1]
	for code, char in replacements.items():
		fileName = fileName.replace(code, char)
	return fileName

def SafeDownloadFile(url, savePath):
	# Baixa arq individual
	tempPath = f"{savePath}.tmp"
	fileName = os.path.basename(savePath)

	try:
		print(f"⌛ Baixando: {fileName[:FILELISTWIDTH]}{'...' if len(fileName) > FILELISTWIDTH else ''}")

		#se já existe arq
		rsmBytePos = os.path.getsize(tempPath) if os.path.exists(tempPath) else 0

		headers = {}
		if rsmBytePos > 0:
			print(f"↻ Retomando download interrompido: {rsmBytePos/1024/1024:.1f} MB")
			headers['Range'] = f'bytes={rsmBytePos}-'

		rsp = requests.get(url, stream=True, timeout=30, headers=headers)
		rsp.raise_for_status()

		tSize = int(rsp.headers.get('content-length', 0)) + rsmBytePos
		download = rsmBytePos

		# Modo 'ab' para append em caso de tetomada 'wb' para novo download
		mode = 'ab' if rsmBytePos > 0 else 'wb'

		with open(tempPath, mode) as f:
			for chunk in rsp.iter_content(chunk_size=8192):
				if chunk:
					f.write(chunk)
					download+=len(chunk)
					if tSize > 0:
						progress = int(50 * download / tSize)
						sys.stdout.write(f"\r[{'=' * progress}{' ' * (50 - progress)}] {download/1024/1024:.1f} MB")
						sys.stdout.flush()

		sys.stdout.write("\n")

		# Se o download completo
		if tSize > 0 and download < tSize:
			raise Exception(f"Download incompleto: {download/tSize} bytes")

		# Renomeia o arq tmp para o nome final
		os.replace(tempPath, savePath)
		print(f"✓ Concluído: {fileName[:FILELISTWIDTH]}{'...' if len(fileName) > FILELISTWIDTH else ''}")
		return True

	except KeyboardInterrupt:
		print(f"\n\n[CTRL] + [C]\n")
		if os.path.exists(tempPath):
			os.remove(tempPath)
		sys.exit(1)

	except requests.exceptions.RequestException as error:
		print(f"\n✗ Erro ao baixar: {fileName} -> {str(error)}")
		if os.path.exists(tempPath):
			os.remove(tempPath)
		return False

	except Exception as error:
		print(f"\n✗ Erro inesperado: {str(error)}")
		if os.path.exists(tempPath):
			os.remove(tempPath)
		return False

def getAllFiles(url, extensions=None):
	# Obtém todos os links de arq da pag da web pode filtrar por ext específicadas se é fornecida
	try:
		print(f"\n🔍 Analisando URL: {url}")
		headers = {
			'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
		}
		rsp = requests.get(url, headers=headers, timeout=30)
		rsp.raise_for_status()
		
		soup = BeautifulSoup(rsp.text, 'html.parser')
		files = []

		for link in soup.find_all('a', href=True):
			href= link['href']
			if not href or href.startswith('#'):
				continue
			fullUrl = urljoin(url, href)
			fileName = href.split('/')[-1]

			if '.' in fileName:
				ext = fileName.split('.')[-1].lower()
				if extensions is None or ext in entensions:
					files.append(fullUrl)

		return list(set(files)) # Rmv urls duplicadas

	except requests.exceptions.RequestException as error:
		print(f"✗ Erro ao acessar a URL: {str(error)}")
		return []
			
	except Exception as error:
		print(f"✗ Erro inesperado ao analisar a pág: {str(error)}")
		return []

def displayFileList(files):
	# Exibe a lista de arq disponíveis de forma formatada
	if not files:
		print("Nenhum arquivo encontrado para download")
		return False

	pHeader(f"📁 Arquivos Disponíveis para download ({len(files)})")

	for i, fileUrl in enumerate(files, 1):
		fileName = decodeUrlFileName(fileUrl)
		wrappedLines = wrap(f"{i:>3}. {fileName}", width=FILELISTWIDTH)
		for line in wrappedLines:
			print(line)

	pFooter()

def downloadFiles(files, outputDir):
	# Gerencia o processo de download dos arquivos
	os.makedirs(outputDir, exist_ok=True)
	tFiles = len(files)
	successCount = 0
	skippedCount = 0
	failedCount = 0

	print(f"\n⏳ Iniciando download de {tFiles} arquivos para: {outputDir}\n")

	for fileUrl in files:
		fileName = decodeUrlFileName(fileUrl)
		savePath = os.path.join(outputDir, fileName)

		if os.path.exists(savePath):
			print(f"⚠ Arquivo existente: {fileName[:FILELISTWIDTH]}{'...' if len(fileName) > FILELISTWIDTH else ''} (pulando)")
			skippedCount+=1
			continue

		if SafeDownloadFile(fileUrl, savePath):
			successCount+=1
		else:
			failedCount+=1

	return {
		'total' : tFiles,
		'success' : successCount,
		'skipped' : skippedCount,
		'failed' : failedCount
	}

def pSummary(stats):
	# Exibe um resume formatado do processo de download
	pHeader("Resumo do Download")

	print(f"• Total de arquivos disponíveis: {stats['total']}")
	print(f"• Arquivos baixados com sucesso: {stats['success']}")
	print(f"• Arquivos que já existiam: {stats['skipped']}")
	if stats['failed'] > 0:
		print(f"• Arquivos com erro no download: {stats['failed']}")    
	pFooter()
	print("\n✅ Concluída!\n")
	return stats

def cleanTmpFiles(outputDir):
	# Rmv arq temp do dir de saída
	tempFiles = [f for f in os.listdir(outputDir) if f.endswith('.tmp')]
	if tempFiles:
		print(f"\n🔍 Limpando arquivos temporários")
		for tempFile in tempFiles:
			try:
				os.remove(os.path.join(outputDir, tempfile))
				print(f"✓ Removido: {tempfile}")
			except Exception as error:
				print(f"✗ Erro ao remover: {tempfile} -> {str(error)}")

if len(sys.argv) <= 1:
	print(r"""
Usage: urldownload.py [-h] ou [--help]

Baixar os arquivos de url

Comandos:
	-h, --help    show this help message and exit
	-o            Diretório para salvar os arquivos padrão: downloads
	-t            Filtrar por extensões específicas ex: zip pdf
	-swf          Mostrar lista de arquivos antes de baixar

Exemplo:
	python urldownload.py https://exemplo.com/arquivos/
	python urldownload.py https://exemplo.com/ -t zip rar -o MeusDownloads
	python urldownload.py https://exemplo.com/ -swf
	""")
	sys.exit(1)

parse = argparse.ArgumentParser(
	description="Baixar os arquivos de url",
	formatter_class=argparse.RawTextHelpFormatter,
	epilog ="Exemplo:\n"
			"  python urldownload.py https://exemplo.com/arquivos/\n"
			"  python urldownload.py https://exemplo.com/ -t zip rar -o MeusDownloads\n"
			"  python urldownload.py https://exemplo.com/ -swf\n"
)

parse.add_argument('url', help='URL contendo os arquivos para download')
parse.add_argument('-o', default='downloads', help='Diretório para salvar os arquivos padrão: downloads')
parse.add_argument('-t', nargs='*', help='Filtrar por extensões específicas ex: zip pdf')
parse.add_argument('-swf', action='store_true', help='Mostrar lista de arquivos antes de baixar')

args = parse.parse_args()

# Ext se fornecidas
exts = [ext.lower().strip('.') for ext in args.t] if args.t else None

# Lista arqs
files = getAllFiles(args.url, exts)

# Mostra Lista
if args.swf:
	displayFileList(files)
	print(f"\nConcluída")
else:
	stats = downloadFiles(files, args.o)
	cleanTmpFiles(args.o)
	pSummary(stats)
