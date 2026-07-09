# Auto-hospedagem no servidor de casa (Tailscale Funnel)

Alternativa ao Netlify (criada quando os créditos de deploy do time se
esgotaram — ver `docs/SESSION_HANDOFF.md`). Serve a mesma PWA a partir de um
servidor Linux próprio, exposto publicamente via **Tailscale Funnel** — sem
precisar de IP público, porta aberta no roteador ou domínio próprio.

O Netlify continua funcionando em paralelo (nada foi desativado); os dois
hosts servem o mesmo conteúdo.

## Pré-requisitos no servidor de casa

- Linux com Node.js instalado (`node --version`; qualquer versão LTS recente serve).
- Tailscale já instalado e conectado à mesma tailnet do usuário.
- Acesso SSH a partir da máquina onde o build é feito.

## 1. Build local

Na máquina de desenvolvimento (não no servidor):

```bash
python scripts/build_pwa.py --saida dist
```

## 2. Copiar os arquivos para o servidor

Substitua `usuario@host` e o caminho de destino pelos seus:

```bash
rsync -avz --delete dist/ usuario@host:/caminho/para/pra-2026-pwa/dist/
rsync -avz server/ lib/ usuario@host:/caminho/para/pra-2026-pwa/server/ /caminho/para/pra-2026-pwa/lib/
```

(Ou `scp -r dist server lib usuario@host:/caminho/para/pra-2026-pwa/` se preferir.)

## 3. Configurar a chave da Groq no servidor (uma vez só)

No servidor, crie `/etc/pra-2026-pwa.env` (fora do repositório, nunca commitado):

```
GROQ_API_KEY=coloque_a_chave_aqui
PORT=8787
```

## 4. Instalar o serviço systemd (uma vez só)

No servidor:

```bash
sudo cp server/pra-2026-pwa.service /etc/systemd/system/
# edite /etc/systemd/system/pra-2026-pwa.service:
#   WorkingDirectory=/caminho/para/pra-2026-pwa (o caminho real)
#   User=seu-usuario (um usuário sem privilégios de root)
sudo systemctl daemon-reload
sudo systemctl enable --now pra-2026-pwa
```

Para atualizações depois (após repetir os passos 1 e 2):

```bash
sudo systemctl restart pra-2026-pwa
```

## 5. Expor publicamente via Tailscale Funnel (uma vez só)

No servidor:

```bash
tailscale funnel --help   # confira a sintaxe da versão instalada
sudo tailscale funnel 8787
```

Pode ser necessário habilitar o recurso "Funnel" para o seu tailnet/nó no
console admin do Tailscale (https://login.tailscale.com/admin/settings/features)
na primeira vez.

A URL pública final tem o formato `https://<nome-do-dispositivo>.<tailnet>.ts.net`.

## Verificação

```bash
# No servidor, testando localmente:
curl http://127.0.0.1:8787/
curl -X POST http://127.0.0.1:8787/api/perguntar -H "Content-Type: application/json" -d '{"pergunta":"tenho direito a PRA?"}'

# De qualquer lugar, depois do Funnel habilitado:
curl https://<dispositivo>.<tailnet>.ts.net/api/perguntar -X POST -H "Content-Type: application/json" -d '{"pergunta":"tenho direito a PRA?"}'
```
