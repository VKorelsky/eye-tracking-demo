# Eye tracking app demo

- Svelte frontend, python backend

# Local set up

Requires `npm` and `uv` to be installed on your machine

1. Clone the repo
2. Prepare frontend

```bash
$ cd fe/
$ npm install
$ npm run build # will compile the frontend and place it in the fe/build dir
```

3. Prepare backend (from root directory)

```bash
$ uv sync
```

4. Set up postgres database

Choose a provider, or use an image from docker. Then:

```bash
$ cp .env.example .env
```

and modify the values to match those of your postgres instance

5. Set up DB schema

To apply the schema changes

```bash
uv run alembic upgrade head
```

6. Run the app

```bash
uv run fastapi dev
```

7. Done
If you make any changes to the frontend, run the npm build again for the changes to be reflected in the frontend