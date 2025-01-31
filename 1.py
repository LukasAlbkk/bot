import logging
from telegram import Update
from telegram.ext import Application, CommandHandler, MessageHandler, filters, CallbackContext

# Ativando logs para debug
logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    level=logging.INFO
)

# Lista global de compras
compras = []

async def start(update: Update, context: CallbackContext):
    """Mensagem inicial do bot"""
    await update.message.reply_text(
        "Olá! Envie mensagens como: 'Arroz 20.50' para adicionar uma compra.\n"
        "Use /subtotal para ver a soma de todas as compras.\n"
        "Use /zerar para apagar todas as compras."
    )

async def registrar_compra(update: Update, context: CallbackContext):
    """
    Captura a mensagem do usuário, tenta entender o item e o valor,
    e armazena na lista global de compras.
    """
    global compras  # Garante que estamos acessando a lista global corretamente

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
        await update.message.reply_text("Não entendi o valor. Tente algo como: 'Pizza 45.90'")
        return
    
    # Pegamos a descrição do item
    try:
        index_valor = palavras.index(str(p))  
    except ValueError:
        index_valor = len(palavras) - 1

    descricao_item = ' '.join(palavras[:index_valor])

    # Adiciona à lista global
    compras.append((descricao_item, valor))

    await update.message.reply_text(f"Registrado: {descricao_item} - R${valor:.2f}")

async def subtotal(update: Update, context: CallbackContext):
    """
    Retorna a soma total de todas as compras.
    """
    global compras  # Garante que estamos acessando a lista global corretamente

    if not compras:
        await update.message.reply_text("Nenhuma compra registrada.")
        return
    
    soma = sum([v for (_, v) in compras])
    
    # Monta um extrato simples
    texto_extrato = "Lista de compras:\n"
    for item, valor in compras:
        texto_extrato += f" - {item}: R${valor:.2f}\n"
    texto_extrato += f"\nSubtotal: R${soma:.2f}"
    
    await update.message.reply_text(texto_extrato)

async def zerar_compras(update: Update, context: CallbackContext):
    """
    Apaga toda a lista de compras.
    """
    global compras  # Garante que estamos acessando a lista global corretamente
    compras.clear()  # Agora limpamos a lista corretamente

    await update.message.reply_text("Lista de compras apagada com sucesso.")

def main():
    """Configuração do bot"""
    token = "7831141421:AAH1vNMwz0H41CzFmMhuasm-ur0Ys_1PZjo"  # Substitua pelo token do seu bot

    app = Application.builder().token(token).build()

    # Adicionando os handlers
    app.add_handler(CommandHandler("start", start))
    app.add_handler(CommandHandler("subtotal", subtotal))
    app.add_handler(CommandHandler("zerar", zerar_compras))
    app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, registrar_compra))

    # Iniciando o bot
    print("Bot está rodando...")
    app.run_polling()

if __name__ == '__main__':
    main()
