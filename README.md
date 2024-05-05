# best-hackath0n-countdown-bot

This repo cotains countdown bot for BEST::HACKath0n 2024.

## How to use?

To start, copy `.env.example` and open it:

```bash
cp .env.example .env
# and open .env with your favourite editor
```

Next, change at least these variables:

```text
BOT_TOKEN=toBeModified

# or set "webhook": false in config.json
WEBHOOK_DOMAIN=toBeModified
WEBHOOK_PORT=toBeModified
```

Follow these steps to run the project:

Using Docker:

1. Build Docker image:

    ```bash
    docker build --tag 'hackathon-bot' .
    ```

2. Create and run Docker container based on tag `'hackathon-bot'`:

    ```bash
    docker run --env-file .env -it 'hackathon-bot' python3 main.py
    ```

3. _(optional)_ If you want to deploy container, you probably want to push the image to Docker Hub:

    > [!NOTE]
    > Be sure to name the tag at step 1 like this: `username/reponame:tagname`

    ```bash
    # 1. Login into Docker (provide credentials interactively)
    docker login
    # 2. Build the image
    docker build --tag 'username/reponame:tagname'
    # 3. Push this tag
    docker push 'username/reponame:tagname'
    ```

On your machine:

1. Activate virtual environment:

    ```bash
    python -m venv venv
    ```

2. Install project dependencies:

    ```bash
    pip install -r requirements.txt
    ```

3. Once done, start the bot:

    ```bash
    python main.py
    ```
