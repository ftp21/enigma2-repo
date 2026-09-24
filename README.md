# ftp21-feed

Feed opkg per i plugin enigma2 di [ftp21](https://github.com/ftp21) (SettingsHub, LCNScanner, ...).

Il contenuto servito (`Packages`, `Packages.gz`, `*.ipk`) vive sul branch `gh-pages`,
pubblicato via GitHub Pages: https://ftp21.github.io/ftp21-feed/

## Come funziona

Ogni repo plugin ha una GitHub Action che, dopo aver pubblicato una release con
il suo `.ipk`, invia un `repository_dispatch` (evento `plugin_release`) a questo
repo con `{repo, tag, asset}`. Il workflow `.github/workflows/add-package.yml`
qui:

1. scarica quell'ipk dalla release del repo sorgente;
2. lo aggiunge al branch `gh-pages`;
3. rigenera `Packages`/`Packages.gz` con `opkg-make-index`;
4. fa commit e push su `gh-pages` (GitHub Pages ripubblica da solo).

## Aggiungere un nuovo repo plugin al feed

Nel workflow di release del plugin, dopo aver creato la release GitHub, aggiungi:

```yaml
- name: Notify package feed
  env:
    GH_TOKEN: ${{ secrets.FEED_DISPATCH_TOKEN }}
  run: |
    gh api repos/ftp21/ftp21-feed/dispatches \
      -f event_type=plugin_release \
      -f "client_payload[repo]=$GITHUB_REPOSITORY" \
      -f "client_payload[tag]=$GITHUB_REF_NAME" \
      -f "client_payload[asset]=$(basename dist/*.ipk)"
```

Serve un secret `FEED_DISPATCH_TOKEN` in quel repo: un personal access token
(fine-grained, scoped solo su questo repo `ftp21-feed`, permesso "Contents:
Read and write") - vedi istruzioni nel repo del plugin o chiedi.

## Uso lato decoder

Su Enigma2, in `/etc/opkg/ftp21-feed.conf` (o via il menu "Aggiornamento software"):

```
src/gz ftp21-feed https://ftp21.github.io/ftp21-feed
```

Poi `opkg update && opkg list-upgradable`.
