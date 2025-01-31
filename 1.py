import logging
from telegram import Update
from telegram.ext import Application, CommandHandler, MessageHandler, filters, CallbackContext
from datetime import datetime

# Ativando logs para debug
logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    level=logging.INFO
)

# Dicionário para armazenar as compras.
compras_por_mes = {}

async def start(update: Update, context: CallbackContext):
    """Mensagem inicial do bot"""
    await update.message.reply_text(
        "Olá! Envie mensagens como: 'Comprei Arroz 20.50'.\n"
        "Use /subtotal para ver a soma do mês."
    )

async def registrar_compra(update: Update, context: CallbackContext):
    """
    Captura a mensagem do usuário, tenta entender o item e o valor,
    e armazena no dicionário.
    """
    mensagem = update.message.text
    palavras = mensagem.split()
    
    # Tenta identificar o valor na mensagem
    valor = None
    for p in reversed(palavras):
        try:
            valor = float(p.replace(',', '.'))  # Se o usuário usar vírgula, trocamos por ponto
            break
        except ValueError:
            continue
    
    if valor is None:
        await update.message.reply_text("Não entendi o valor. Tente algo como: 'Comprei Pizza 45.90'")
        return
    
    # Pegamos a descrição do item
    try:
        index_valor = palavras.index(str(p))  
    except ValueError:
        index_valor = len(palavras) - 1

    if palavras[0].lower() == "comprei":
        descricao_item = ' '.join(palavras[1:index_valor])
    else:
        descricao_item = ' '.join(palavras[:index_valor])

    # Pega o mês/ano atual
    mes_ano = datetime.now().strftime("%m-%Y")

    if mes_ano not in compras_por_mes:
        compras_por_mes[mes_ano] = []

    compras_por_mes[mes_ano].append((descricao_item, valor))

    await update.message.reply_text(f"Registrado: {descricao_item} - R${valor:.2f}")

async def subtotal(update: Update, context: CallbackContext):
    """
    Retorna a soma do mês atual.
    """
    mes_ano = datetime.now().strftime("%m-%Y")
    
    if mes_ano not in compras_por_mes or len(compras_por_mes[mes_ano]) == 0:
        await update.message.reply_text("Nenhuma compra registrada neste mês.")
        return
    
    lista_compras = compras_por_mes[mes_ano]
    soma = sum([v for (_, v) in lista_compras])
    
    # Monta um extrato simples
    texto_extrato = "Compras do mês:\n"
    for item, valor in lista_compras:
        texto_extrato += f" - {item}: R${valor:.2f}\n"
    texto_extrato += f"\nSubtotal: R${soma:.2f}"
    
    await update.message.reply_text(texto_extrato)

def main():
    """Configuração do bot"""
    token = "7831141421:AAH1vNMwz0H41CzFmMhuasm-ur0Ys_1PZjo"  # Substitua pelo token do seu bot

    app = Application.builder().token(token).build()

    # Adicionando os handlers
    app.add_handler(CommandHandler("start", start))
    app.add_handler(CommandHandler("subtotal", subtotal))
    app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, registrar_compra))

    # Iniciando o bot
    print("Bot está rodando...")
    app.run_polling()

if __name__ == '__main__':
    main()
