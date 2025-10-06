import random


class Player:
    def __init__(self, name):
        """Initializes a player with a name and a guess."""
        self.name = name
        self.guess = None

    def make_guess(self):
        """Prompts the player to enter their guess."""
        while True:
            guess = input(f"{self.name}, enter your guess (Heads/Tails): ").strip().capitalize()
            if guess in ['Heads', 'Tails']:
                self.guess = guess
                break
            else:
                print("Invalid input. Please enter 'Heads' or 'Tails'.")


class CoinFlippingGame:
    def __init__(self):
        """Initializes the game."""
        self.player1 = Player("Player 1")
        self.player2 = Player("Player 2")
        self.result = None

    def flip_coin(self):
        """Simulates flipping a coin."""
        return random.choice(['Heads', 'Tails'])

    def set_player2_guess(self):
        """Sets Player 2's guess based on Player 1's guess."""
        self.player2.guess = 'Tails' if self.player1.guess == 'Heads' else 'Heads'
        print(f"{self.player2.name}'s guess is automatically set to: {self.player2.guess}")

    def determine_winner(self):
        """Determines and displays the winner based on guesses and result."""
        if self.player1.guess == self.result and self.player2.guess == self.result:
            print("Both players guessed correctly! It's a tie!")
        elif self.player1.guess == self.result:
            print(f"{self.player1.name} guessed correctly! {self.player2.name} loses.")
        elif self.player2.guess == self.result:
            print(f"{self.player2.name} guessed correctly! {self.player1.name} loses.")
        else:
            print("Both players guessed incorrectly! No one wins.")

    def play(self):
        """Main function to play the coin flipping game."""
        print("Welcome to the Coin Flipping Game!")

        # Get Player 1's guess
        self.player1.make_guess()

        # Set Player 2's guess based on Player 1's guess
        self.set_player2_guess()

        # Flip the coin
        self.result = self.flip_coin()
        print(f"The result of the coin flip is: {self.result}")

        # Determine and display results
        self.determine_winner()


if __name__ == "__main__":
    game = CoinFlippingGame()
    game.play()