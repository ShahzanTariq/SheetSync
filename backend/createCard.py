from transformer import Transformer


def TD_account (inputFile):
    tdCard = Transformer(card_name="TD", date_col=1, amount_col=4,description_col=3,category_col=6, header=True)
    tdCard.reformat_csv(inputFile)