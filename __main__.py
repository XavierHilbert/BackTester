import constants, data_base, variables, model, analyze


def create_stocks(file: str) -> None:
    """Updates symbols in data base."""
    file_handle = open(file, constants.READ_TYPE, encoding=constants.ENCODING)
    for symbol in file_handle:
        data_base.SYMBOLS.append(symbol.strip())
    file_handle.close()


def analyze_data(data: list):
    """Sends data to be analyzed."""
    analyze.calc_confiendece_interval(data)
    analyze.graph(data)


def append_data_base():
    """Appends the net percent lists in data base."""
    for net_amount in data_base.NET_AMOUNT:
        net_percent: float = (net_amount/constants.MAX_CASH_TO_SPEND) * 100.0
        data_base.NET_PERCENT.append(net_percent) 
    data_base.NET_PERCENT_NO_ZEROS = [x for x in data_base.NET_PERCENT if x != 0.0]
    data_base.NET_PERCENT_LOSS = [x for x in data_base.NET_PERCENT if x < 0.0]


def main():
    """Entrypoint."""
    create_stocks(variables.FILE)

    back_test = model.BackTester()
    back_test.simulate()

    append_data_base()

    print(f"{(1.0 - len(data_base.NET_PERCENT_LOSS)/len(data_base.NET_PERCENT_NO_ZEROS)) * 100} % of days are winning days!")
    # analyze net percent
    print("For net percent:")
    analyze_data(data_base.NET_PERCENT)
    # analyze net percent exlcuding days where no trades were placed
    print("For only losses:")
    analyze_data(data_base.NET_PERCENT_LOSS)


if __name__ == "__main__":
    main()