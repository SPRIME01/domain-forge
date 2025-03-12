## MkDocs Documentation

- View documentation locally: Run `uv pip run mkdocs serve` and visit http://127.0.0.1:8000
- Build documentation: Run `uv pip run mkdocs build` to generate static site in the site/ directory
- Deploy documentation: If using GitHub Pages, run `uv pip run mkdocs gh-deploy`
- The documentation will automatically include your docstrings and generate API reference documentation based on your code.
- Generate and serve the documentation.
  Run `uv pip run mkdocs serve` to view documentation locally.
- To build the documentation for production:
  Run `uv pip run mkdocs build` to generate static site in the site/ directory.

## API Documentation

To run the FastAPI application:
`uvicorn domainforge.infrastructure.app:app --reload`

The server is now running successfully! You can access the Swagger UI documentation by opening your web browser and navigating to:

http://127.0.0.1:8000/api/docs

This will show you the interactive API documentation where you can:

The documentation is automatically generated from your FastAPI route definitions, including:

All API endpoints

- Request/response models
- Query parameters
- Path parameters
- Request bodies
- Response schemas

See all available API endpoints
Test the endpoints directly from the browser
View request/response schemas
Execute API calls
For a more styled alternative documentation view, you can also visit: http://127.0.0.1:8000/api/redoc

If you need to examine the raw OpenAPI specification, it's available at: http://127.0.0.1:8000/api/openapi.json

The server is running in development mode with auto-reload enabled, so any changes you make to the code will automatically restart the server.

To stop the server when you're done, just press Ctrl+C in the terminal.

# flow

Yes, looking at your documentation.yml file, you have a complete CI/CD workflow set up that automatically builds and deploys your documentation when you push to main or create a pull request. Let me break down what happens:

1. Trigger Conditions:

   - Runs on pushes to the main branch
   - Runs on pull requests targeting the main branch

2. Environment Setup:

   - Uses Ubuntu latest
   - Sets up Python 3.13
   - Sets up Node.js 21
   - Configures caching for both uv (Python) and npm (Node.js) dependencies

3. Build Process:
   1. Installs uv
   2. Installs Python dependencies with uv
   3. Installs Node.js dependencies with npm
   4. Generates TypeDoc documentation
   5. Builds Storybook
   6. Generates API Reference with gen_ref_pages.py
   7. Builds MkDocs documentation
   8. Deploys documentation to GitHub Pages
4. Deployment:

   - Uses the peaceiris/actions-gh-pages@v3 action
   - Only deploys when pushing to main (not on PRs)
   - Deploys the site directory to GitHub Pages
   - Uses force_orphan: true for clean deployments
     This means your documentation will:

   - Build and validate on every PR (helping catch issues before merge)
   - Automatically deploy to GitHub Pages when merged to main
   - Include:
     - API documentation (Python + TypeScript)
     - Storybook UI component documentation
     - MkDocs main documentation site

The workflow will integrate:

- TypeScript/React component docs via TypeDoc
- UI component examples via Storybook
- Python API docs via mkdocstrings
- General documentation via MkDocs with Material theme
