# Urldownload
#### **Baixar arquivos de forma automatizada pela url**
---
## Instalação
**Para começar a usar o urldownload.py**
### Clone o repositório
```bash
        git clone https://github.com/izaqux/urldownload.git

        cd urldownload
```
---
<pre>
<b>
usage: urldownload.py [-h] ou [--help]

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
</b>
</pre>