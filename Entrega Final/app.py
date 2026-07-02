from flask import Flask, render_template, request
from flask_mysqldb import MySQL

app = Flask(__name__)

# CONEXÃO MYSQL
app.config['MYSQL_HOST'] =
app.config['MYSQL_USER'] =
app.config['MYSQL_PASSWORD'] =
app.config['MYSQL_DB'] =

mysql = MySQL(app)


@app.route('/', methods=['GET', 'POST'])
def index():

    empresa = None
    erro = None
    historico2 = []

    if request.method == 'POST':

        # pega cnpj digitado
        cnpj = request.form.get('cnpj')

        # remove caracteres especiais
        cnpj = cnpj.replace('.', '').replace('/', '').replace('-', '')

        # validação
        if not cnpj.isdigit() or len(cnpj) != 14:
            erro = 'CNPJ inválido'

            return render_template(
                'index.html',
                empresa=empresa,
                erro=erro,
                historico2=historico2
            )

        # divisão cnpj
        cnpj_basico = cnpj[:8]
        cnpj_ordem = cnpj[8:12]
        cnpj_dv = cnpj[12:]

        try:

            cursor = mysql.connection.cursor()

            sql = """
                SELECT
                    nome_fantasia,
                    situacao_cadastral.descricao AS situacao_cadastral,
                    logradouro,
                    numero,
                    bairro,
                    municipios.descricao AS municipio,
                    uf,
                    cep,
                    cnaes.descricao AS cnae_fiscal_principal,
                    ddd1,
                    telefone1,
                    correio_eletronico
                FROM estabelecimentos
                
                LEFT JOIN municipios
                ON estabelecimentos.municipio = municipios.codigo
                
                LEFT JOIN cnaes 
                ON estabelecimentos.cnae_fiscal_principal = cnaes.codigo

                LEFT JOIN situacao_cadastral 
                ON estabelecimentos.situacao_cadastral = situacao_cadastral.codigo

                WHERE
                    cnpj_basico = %s
                    AND cnpj_ordem = %s
                    AND cnpj_dv = %s
            """

            cursor.execute(sql, (cnpj_basico, cnpj_ordem, cnpj_dv))

            pesquisa_cnpj = cursor.fetchone()

            if pesquisa_cnpj:

                empresa = {
                    'nome_fantasia': pesquisa_cnpj[0],
                    'situacao': pesquisa_cnpj[1],
                    'logradouro': pesquisa_cnpj[2],
                    'numero': pesquisa_cnpj[3],
                    'bairro': pesquisa_cnpj[4],
                    'municipio': pesquisa_cnpj[5],
                    'uf': pesquisa_cnpj[6],
                    'cep': pesquisa_cnpj[7],
                    'cnae': pesquisa_cnpj[8],
                    'ddd1': pesquisa_cnpj[9],
                    'telefone1': pesquisa_cnpj[10],
                    'correio_eletronico': pesquisa_cnpj[11]
                }

                insert_historico = """
                    INSERT INTO historico2 (
                        cnpj_basico,
                        cnpj_ordem,
                        cnpj_dv,
                        nome_fantasia
                    )
                    VALUES (%s, %s, %s, %s)
                """

                cursor.execute(
                    insert_historico,
                    (
                        cnpj_basico,
                        cnpj_ordem,
                        cnpj_dv,
                        pesquisa_cnpj[0]
                    )
                )

                mysql.connection.commit()
                
                cursor.execute("""
                    SELECT
                        cnpj_basico,
                        cnpj_ordem,
                        cnpj_dv,
                        nome_fantasia
                    FROM historico2
                    ORDER BY id_historico DESC
                    LIMIT 10
                """)

                historico2 = cursor.fetchall()

            else:
                erro = 'CNPJ não encontrado'

            cursor.close()

        except Exception as e:
            erro = f'Erro: {str(e)}'

    return render_template(
        'index.html',
        empresa=empresa,
        erro=erro,
        historico2=historico2
    )

    


if __name__ == '__main__':
    app.run(debug=True)
