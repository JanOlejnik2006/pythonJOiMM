def print_menu():
    print("\n" + "=" * 40)
    print("   CINESTREAM - KOLEKCJA FILMOWA   ")
    print("=" * 40)
    print("1.Wyswietl kolekcje")
    print("2.Dodaj film")
    print("3.Filtruj po gatunku")
    print("4.Wyjscie z programu")
    print("-" * 40)




def handle_menu_choice(choice: str) -> bool:
    match choice.strip():
        case "1" | "2" | "3":
            print("Ta opcja bedzie dostypna wkrotce.")
        case "4" | "q" | "exit":
            print("Zamykanie programu do widzenia.")
            return False
        case _:
            print("Blad: Nieznana opcja. Wybierż wartosc od 1 do 4.")
    return True



def main():
    running = True
    while running:
        print_menu()
        user_choice = input("Wybierz opcje [1-4]: ")
        running = handle_menu_choice(user_choice)


if __name__ == "__main__":
    main()