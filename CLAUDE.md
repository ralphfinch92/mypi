# mypi

This repo is only the old Raspberry Pi dashboard. If the task is about Styled By Shaynie, Us2You or Latest and Greatest, it is in the wrong repo: see below.

## Ralph's projects — read this first

Ralph (ralphfinch92 on GitHub) runs several separate projects. Don't mix them up.

| Project | What it is | Code |
|---|---|---|
| **Styled By Shaynie** | Website + booking + admin panel for Shaynie, a hairdresser in Pound Hill, Crawley. Shaynie is Ralph's brother's partner. Live at styled-by-shaynie.co.uk. | GitHub `ralphfinch92/styled-by-shaynie`; on the Mac at `~/Documents/styled-by-shaynie` |
| **Us2You** | Ralph's own mobile phone/console repair business. Website us2you.co.uk with an admin panel (tile-style home; Ralph likes tiles, not lists). | On the Mac at `~/Documents/us2you` |
| **Latest and Greatest** | An automated Facebook page (Latest and Greatest News) that runs alongside a website. | On the Mac at `~/Documents/latest-and-greatest` |
| **mypi** | An old Raspberry Pi dashboard. Nothing else lives here. | GitHub `ralphfinch92/mypi` |

### Notes
- "Latest and Greatest Project" is also the name of the long-running Claude chat on Ralph's Mac. Being that chat doesn't make work in it about Latest and Greatest.
- Styled By Shaynie deploys from the Mac with the wrangler binary that happens to live in the Us2You folder:
  `~/Documents/us2you/node_modules/.bin/wrangler pages deploy public --project-name styled-by-shaynie --branch main`
  That command only touches Shaynie's site. Pushing to GitHub does NOT deploy anything.
- Ralph's preferences: write code one file at a time, say "file N of M", name the file and where it goes, keep explanation short. Admin panels use square tiles, not lists.
