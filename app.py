import psycopg2

try:
    conn = psycopg2.connect(
        host="localhost",
        database="enade",
        user="postgres",
        password="geas9090"
    )

    cur = conn.cursor()

    cur.execute("""
        SELECT id
        FROM questao
        WHERE numero = %s
    """, (1,))

    questao_id = cur.fetchone()[0]

    cur.execute("""
        INSERT INTO gabarito (questao_id, resposta)
        VALUES (%s, %s)
        ON CONFLICT (questao_id) DO NOTHING
    """, (
        questao_id,
        "A"
    ))

    conn.commit()

    print("Gabarito inserido com sucesso!")

    cur.close()
    conn.close()

except Exception as e:
    print("Erro:", e)