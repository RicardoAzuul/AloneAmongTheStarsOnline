# AloneAmongTheStarsOnline
A C# webapp for playing Alone Among The Stars

Alone Among The Stars is designed by Takuma Okada: https://noroadhome.itch.io/alone-among-the-stars

To get familiar with using C# for webapps, I decided to create a webapp of this little game.

Created with some help from this Youtube vid: https://www.youtube.com/watch?v=BfEjDD8mWYg&t=646s

# Functionality

The idea is to be able to play Alone Among the Stars in the browser. To do so:
Find a new planet with unique features
- be able to roll a d6 --> the number of unique features
- the result rolled is how many cards are drawn from a standard deck of cards, face down
- so we need to be able to draw cards from a deck

To discover:
- roll a d6:
    - 1-2: arduous to get to
    - 3-4: come upon it suddenly
    - 5-6: spot as you're resting

Suit and rank determine discovery:
- need to match the card's suit and rank to a small list of results

We need to be able to journal this:
- description of discovery
- reaction to discovery
- once all things on a planet have been discovered, name or number planet and either keep going or stop.

We need to be able to save the journals.

# Creating a new dotnet app

https://docs.microsoft.com/en-us/dotnet/core/tools/dotnet-new-sdk-templates#web-options

ASP.NET Core Web App (Model-View-Controller) ```dotnet new mvc --auth individual```

# Running the app

```dotnet run```