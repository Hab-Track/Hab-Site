# Project Overview

**Hab Track** is a tool that keeps track of changes in Habbo and various retro servers.<br>
It monitors changes for badges, clothing, furniture, and effects. When a change is detected, it sends a message to the [Discord server](https://discord.gg/7SvKF6wpss).<br>
The system currently only detects text-based changes, so it will not detect modifications in images.

## Key Features

- **[Discord Server](https://discord.gg/7SvKF6wpss):** Get updates and notifications containing all changes between texts and new images
- **[Interactive Graphs](/graphs):** Visualize asset statistics over time
- **[Advanced Search](/search):** Find specific assets across all tracked retros
- **[API](/api/docs):** Public and free API for accessing all tracked data

## Project Components

### Discord Server

- The Discord server is the center of the project, where most activities and updates happen
- You can suggest new retros, get a list of already tracked ones and retros that aren't supported
- Receive updates when changes are detected on Habbo with [Habbo Track](https://github.com/hab-track/habbo-track)
- A Discord bot with various utilities
- Daily updates with all the new stats for each retro in the [dedicated channel](https://discord.com/channels/1088116219984478228/1166103150994927746)

### Graphs

- The statistics used for generating the graphs are updated once a day
- Enjoy many interactive features thanks to [Plotly](https://plotly.com/chart-studio-help/getting-to-know-the-plotly-modebar/)

### Search

- The search page allows you to find specific assets across all tracked retros
- View image previews of assets
- Search by name, title, description, retro, or asset type to find exactly what you're looking for

### API

- The API is free and public with no rate limits (unless maybe Vercel...)
- Basic functionality is currently available, feel free to suggest new features or create PRs

## Open Source

Hab Track is open source and available on [GitHub](https://github.com/hab-track/)