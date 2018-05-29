# Script para Geração de TMS de Imagens Rapideye

## Sumário
- Objetivo
- Pré requisitos de sistema
- Pré requisitos do script
- Funcionamento do script completo
- Funcionamento do script *footprint.py*
- Funcionionamento do script generate_tms.py
- Arquivo de configurações
- Passo a passo do script completo

## Objetivo

- Este script tem como objetivo gerar TMS's de imagens rapideye e salva-las em banco.
- O processamento das imagens pode ser em fila ou em paralalelo, com no máximo 10 threads.
- Esta ferramenta funciona com todas as suas fucionalidades ao utilizar o arquivo **processing.py**.
Se preferir utilizar suas funcionalidades de forma isolada, basta utilizar os scripts **footprint.py** e/ou **generate_tms.py**.

> #### Nota
> - O footprint gerado é baseado em um VRT mascarado, logo, caso a imagem esteja corrompida, isso será ignorado e o footprint será gerado normalmente.
>
> - Caso os lotes de processamento sejam maior do que 10, o script irá processar paralelamente com 10 threads.
> 
> - Este script assume que as imagens rapideye já estejam compostas com algumas bandas, para que seja possível ocorrer recomposição de bandas.

## Pré Requisitos de Sistema
- Instalar gdal >= 2.x
- Instalar dans-gdal-scripts
	- https://github.com/gina-alaska/dans-gdal-scripts
- Possuir um ambiente virtual com o python35 como default, e python27


## Pré Requisitos do Script
- Instalar as libs contidas em process_re/requirements.txt

```shell
pip install -r requirements.txt
```
> #### Nota
>- Este ambiente virtual deve possuir a lib gdal disponível para o python35 e python 27

<br>

### Funcionamento do script completo (utilizando processing.py):
>##### Objetivo:
> - *Processar um lote de imagens baseado na constante FILE_ALL_RAPIDEYE* (movendo para outro diretório ou não) O processamento pode ser em paralelo ou em fila.
> - *Processar apenas uma imagem passada como argumento de linha de comando* (movendo para outro diretório ou não).
> 

- Reorganização e recomposição de bandas para 3 5 2 ao lado do .tif (definição das bandas estão em constans.py)
- Geração de TMS's
- Aplicação de constraste streach
- Geração de footprint para obtenção de geometria para inserção em banco
- Geração de PNG (quicklook)
- Obtenção do path da imagem
- Obtenção do path do RGB 
- Obtenção do path do PNG 
- Obtenção do path do xml do tms 
- Obtenção do percentual de nuvens
- Inserção destas informações em banco
- geração de logs de sucesso e erro para cada processamento
- Será movido as imagens do path de origem para um path de destino (a origem e destino estão definidos em constants.py).

#### Formas de uso:
- Processameto baseado em um lote de imagens definido na constante *FILE_ALL_RAPIDEYE*
```shell
python processing.py -dirImgs /path/to/rapideye/4a_cobertura/
```

- Processameto baseado em um lote de imagens definido na constante *FILE_ALL_RAPIDEYE* e movendo para outro diretório (o destino está definido na constante DESTINY_RAPIDEYE)
```shell
python processing.py -dirImgs /path/to/rapideye/4a_cobertura/ -move 1
```


- Processameto baseado em um lote de imagens definido na constante *FILE_ALL_RAPIDEYE* e movendo para outro diretório (o destino está definido na constante DESTINY_RAPIDEYE) e utilizando threads.
```shell
python processing.py -dirImgs /path/to/rapideye/4a_cobertura/ -move 1 -thr 1
```

- Processameto de apenas uma imagem
```shell
python processing.py -dirImgs /path/to/dir_img/ -oneImg 1
```

- Processameto de apenas uma imagem e movendo para outro diretório (o destino está definido na constante DESTINY_RAPIDEYE) 
```shell
python processing.py -dirImgs /path/to/dir_img/ -oneImg 1 -move 1
```

<br>

### Funcionamento do script *footprint.py*
>##### Objetivo:
> - *Gerar o footprint do tif em um shapefile.*
> - *Gerar um footprint em um shapefile e exportar a geometria em um arquivo WKT.*

- Poligonizar e reprojetar um tif rapideye
- Caso necessário, solicitar exportação de geometria gerada, como wkt 

#### Formas de uso:
- Geração de shapefile
```shell
python footprint.py -imgIn /path/to/img.tif -footOut /path/to/result/my_foot
```
- Geração de shapefile com exportação de wkt
```shell
python footprint.py -imgIn /path/to/img.tif -footOut /path/to/result/my_foot -wkt 1
```

### Funcionionamento do script *generate_tms.py*
>##### Objetivo:
> - *Gerar o TMS de um imagem rapideye*

- Reorganização e recomposição de bandas
- Aplicação de constraste streach
- Geração de TMS's

#### Forma de uso:

```shell
python generate_tms.py -imgPathIn /path/to/img.tif -br 3 -bg 5 -bb 2 -rgbPathOut /path/to/dir_rgb -zoomMin 2 -zoomMax 5 -link http://127.0.0.1/imgs -dirTms /path/to/dir_tms
```

<br>

## Arquivo de configurações *constants.py*
- **DESTINY_RAPIDEYE** - Diretório de destino para onde as imagens serã movidas **<'/home/user/'>**
- **TOTAL_PART** - Valor estático para precher o campo *total_part* da tabela. Este valor é estático pois, a geração de footprint será baseado em um .vrt mascarado, logo, qualquer falha nos pixels da imagem será ignorado e a poligonização será gerada normalmente. **<1>**
- **FILE_ALL_RAPIDEYE** - Path de arquivo com todas as imagens a serem processada. É aconselhado que seja passa apenas um arquivo com um lote de imagens por vez. **<"/home/user/lotes/lote_1.txt">**
- **OUTSIZE_RGB** - Percentual da resolução de saída da imagem  <**10**>
- **B52_PATH** = Path para o ponto de montagem do b52 <**\\\\10.1.25.66\\b52_imagens\\rapideye\\**>
- **DIR_PNG** - Path do diretório que serão gerados os PNG's. **<"/home/user/png">**
- **DIR_PNG_TO_DB** - Path do png que será inserido em banco (é útil para pontos de montagens). **<<span>http:<span>//10.1.25.x/imagens/png/>**
- **DIR_TMS** = Path do diretório que serão gerados os TMS's. **<"/home/user/tms">**
- **URL_TMS** = Url do TMS <<span>http:</span>//10.1.8.69/TMS-TESTE>
- **ZOOM_MIN** = Valor mínimo de zoom para o TMS <**2**>
- **ZOOM_MAX** = Valor máximo de zoom para o TMS <**18**>
- **BAND_R** = Banda Red <**3**>
- **BAND_G** = Banda Green <**5**>
- **BAND_B** = Banda Blue <**2**>
- **HOSTADDR** = Ip do servidor da base de dados <**10.1.8.X**>
- **USER** = Usuário para acesso a base de dados <**postgres**>
- **PASSWORD** = Senha para acesso a base de dados <**123456**>
- **DATABASE** = Nome da base de dados <**my_siscom**>
- **SCHEMA** = Schema para a tabela <**ibama**>
- **TABLENAME_RAPIDEYE_CATALOG** = Tabela de imagens rapideye <**img_catalogo_rapideye_a**>

# Passo a Passo

## Processamento em Lote
- ***1*** - Gerar os arquivos de lote com as imagens necessárias. Dentro de generate_lot faça:
```shell
python create_txt_with_lot.py path/rapideye/imgs/
```
> Com isto, será criado arquivos com no máximo 1000 imagens com o nome das imagens. Estes 
> arquivos serã gerados dentro do diretório "generate_lot/files"
- ***2*** - Após gerado os arquivos com lote das imagens, configure o arquivo de configuração *constants.py*, com as informações das imagens, dados de conexão e, o arquivo de lote a ser processado (*FILE_ALL_RAPIDEYE* - deve possuir o caminho absoluto).
> Caso seja necessário mover a imagem, passe um path absoluto do destino para a constante *DESTINY_RAPIDEYE*, e execute o script de processamento passando o parâmetro "-move 1" sem aspas.

- ***3*** - Após configurado o arquivo *constants.py*, execute o arquivo de processamento passando o diretório onde se encontra as imagens que estão listadas no lote a ser processado
(*FILE_ALL_RAPIDEYE*).

```shell
python processing.py -dirImgs path/rapideye/imgs/ -thr 1 -move 1
```
> O processamento em paralelo (-thr 1) é opcional.

## Processamento Individual
- ***1*** - Para processar apenas uma imagem, execute o script de processamento, passando o path para a imagem no parâmetro "-dirImgs" e passe o parâmetro "-oneImg 1". Ambos sem aspas.
```shell
python processing.py -dirImgs path/to/rapideye/2032526_2014-07-31_RE4_3A_315082_CR -oneImg 1
```
