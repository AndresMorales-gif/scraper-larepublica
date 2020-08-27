import requests
import lxml.html as html
import os
import datetime
import logging
logging.basicConfig(level=logging.INFO)



logger = logging.getLogger(__name__)

HOME_URL = 'https://www.larepublica.co'

XPATH_LINK_TO_ARTICLE = '//div[contains(@class,"itle")]//text-fill/a/@href'
XPATH_TITLE = '//div[@class="mb-auto"]/text-fill/a/text()'
XPATH_SUMMARY = '//div[@class="lead"]/p/text()'
XPATH_DATE = '//span[@class="date"]/text()'
XPATH_AUTHOR = '//div[@class="autorArticle"]/p/text()'
XPATH_BODY = '//div[@class="html-content"]/p/text()'


def parse_notice(link, today):
	try:
		response = requests.get(link)
		if response.status_code == 200:
			notice = response.content.decode('utf-8')
			parsed = html.fromstring(notice)
			
			try:
				title = parsed.xpath(XPATH_TITLE)[0]
				title = title.replace('\"','')
				summary = parsed.xpath(XPATH_SUMMARY)[0]
				date = parsed.xpath(XPATH_DATE)[0]
				author = parsed.xpath(XPATH_AUTHOR)[0]
				body = parsed.xpath(XPATH_BODY)
			except IndexError:
				logger.warning(f'No se pudo encontrar datos para el link {link}')
				with open(f'{today}/logger-{today}.txt', 'a', encoding='utf-8') as f:
					f.write(f'No se pudo encontrar datos para el link {link}')
					f.write('\n')
					f.close()
				return 0

			with open(f'{today}/{title}.txt', 'w', encoding='utf-8') as f:
				f.write(title)
				f.write('\n')
				f.write(f'Autor: {author}, fecha: {date}')
				f.write('\n\n')
				f.write(summary)
				f.write('\n\n')
				for p in body:
					f.write(p)
					f.write('\n')

			return 1

		else:
			raise ValueError(f'Error: {response.status_code}')
	except ValueError as ve:
		logger.warning(ve)
		return 0


def parse_home():
	try:
		logger.info(f'Intentando obtener el html de la url {HOME_URL}')
		response = requests.get(HOME_URL)
		logger.info(f'Estatus code: {response.status_code}')
		if response.status_code == 200:
			home = response.content.decode('utf-8')
			parsed = html.fromstring(home)			
			logger.info('Buscando los links de los articulos')
			links_to_notices = parsed.xpath(XPATH_LINK_TO_ARTICLE)			
			logger.info(f'Se han encontrado {len(links_to_notices)} articulos')
			today = datetime.date.today().strftime('%d-%m-%Y')

			if not os.path.isdir(today):
				logger.info(f'Creacion de la carpeta {today}')
				os.mkdir(today)
			
			with open(f'{today}/logger-{today}.txt', 'w', encoding='utf-8') as f:
				f.write(f'Se han encontrado {len(links_to_notices)} articulos')
				f.write('\n')
			articles_val = 0	

			for link in links_to_notices:				
				logger.info(f'Obteniendo la informacion del link: {link}')
				articles_val += parse_notice(link, today)
			
			logger.info(f'Hay {articles_val} articulos validos')
			with open(f'{today}/logger-{today}.txt', 'a', encoding='utf-8') as f:
				f.write(f'Hay {articles_val} articulos validos')
				f.close()

		else:
			raise ValueError(f'Error: {response.status_code}')
	except ValueError as ve:
		logger.warning(ve)


def run():
	parse_home()


if __name__=='__main__':
	run()