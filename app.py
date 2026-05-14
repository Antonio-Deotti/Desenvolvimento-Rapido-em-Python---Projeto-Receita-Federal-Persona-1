from flask import Flask, render_template, request
import requests

app = Flask(__name__)

@app.route('/', methods=['GET', 'POST'])
def index():

    empresa = None
    erro = None

    if request.method == 'POST':

        #requisição do valoe preenchido no formulario
        cnpj = request.form.get('cnpj')

        #excluir carcteres especificos para url dinamica
        cnpj = cnpj.replace('.', '').replace('/', '').replace('-', '')

        #url dinamica para consulta no banco de dados da api
        url = f'https://brasilapi.com.br/api/cnpj/v1/{cnpj}'

        try:
            
            #requisição dos dados da api
            response = requests.get(url)

            if response.status_code != 200:
                erro = 'CNPJ não encontrado'
            else:
                #converte retorno da api em dicionario python
                dados = response.json()

                empresa = {
                    'razao_social': dados.get('razao_social'),
                    'nome_fantasia': dados.get('nome_fantasia'),
                    'situacao': dados.get('descricao_situacao_cadastral'),
                    'logradouro': dados.get('logradouro'),
                    'numero': dados.get('numero'),
                    'bairro': dados.get('bairro'),
                    'municipio': dados.get('municipio'),
                    'uf': dados.get('uf'),
                    'cep': dados.get('cep'),
                    'cnae': dados.get('cnae_fiscal_descricao')
                }

        except Exception as e:
            erro = f'Erro: {str(e)}'

    return render_template(
        'index.html',
        empresa=empresa,
        erro=erro
    )

if __name__ == '__main__':
    app.run(debug=True)
