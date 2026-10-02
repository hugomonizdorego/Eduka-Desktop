#!/usr/bin/env python3
"""Write usr/share/edukasaun-desktop/i18n/<lang>.json from catalog_full.py
(Portuguese, Indonesian, Tetun) and catalog_core.py (Malay, Filipino, Thai,
Vietnamese, Chinese). Brazilian Portuguese is pt.json plus pt_BR.json with
only the words that differ.

    python3 tools/i18n/build-catalogs.py
"""
import json, re, sys
from pathlib import Path

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE))
from catalog_full import FULL
from catalog_core import CORE, LANGS
from catalog_0920 import NEW
from fix_tetun import TETUN_FIX, TETUN_WORDS

OUT = HERE.parents[1]/'usr'/'share'/'edukasaun-desktop'/'i18n'

# European -> Brazilian Portuguese, whole words only.
PT_BR = [
    ('Ecrã', 'Tela'), ('ecrã', 'tela'), ('Definições', 'Configurações'), ('definições', 'configurações'),
    ('Predefinições', 'Configurações padrão'), ('predefinição', 'padrão'), ('Predefinição', 'Padrão'),
    ('ficheiros', 'arquivos'), ('ficheiro', 'arquivo'), ('Ficheiros', 'Arquivos'), ('Ficheiro', 'Arquivo'),
    ('Utilizador', 'Usuário'), ('utilizador', 'usuário'), ('Utilizadores', 'Usuários'), ('utilizadores', 'usuários'),
    ('Guardar', 'Salvar'), ('guardar', 'salvar'), ('guardadas', 'salvas'), ('guardada', 'salva'),
    ('guardados', 'salvos'), ('guardado', 'salvo'), ('Guardado', 'Salvo'), ('Guarde', 'Salve'),
    ('Prima', 'Pressione'), ('prima', 'pressione'), ('Terminar sessão', 'Sair'),
    ('Terminar a sessão do', 'Sair do'), ('palavra-passe', 'senha'), ('Palavra-passe', 'Senha'),
    ('controlo', 'controle'), ('A salvar', 'Salvando'), ('a salvar', 'salvando'),
    ('Transferir', 'Baixar'), ('rato', 'mouse'), ('Rato', 'Mouse'), ('ecrãs', 'telas'),
    ('gestor', 'gerenciador'), ('Gestor', 'Gerenciador'), ('a reiniciar', 'reiniciando'),
    ('a ser reconstruída', 'sendo reconstruída'), ('Repor', 'Redefinir'), ('repostas', 'restauradas'),
    ('Aceder', 'Acessar'), ('aceder', 'acessar'), ('Ativar', 'Ativar'), ('equipa', 'equipe'),
]

# 'Ecrã' is masculine, 'tela' feminine.
PT_BR_AFTER = [
    ('o tela', 'a tela'), ('O tela', 'A tela'), ('do tela', 'da tela'), ('neste tela', 'nesta tela'),
    ('Novo tela', 'Nova tela'), ('novo tela', 'nova tela'), ('tela inteiro', 'tela inteira'),
    ('tela de entrada atualizado', 'tela de entrada atualizada'), ('Tela de entrada atualizado', 'Tela de entrada atualizada'),
    ('só pode ser alterado', 'só pode ser alterada'), ('Redefinir predefinições', 'Restaurar padrões'),
]
# 'ligado' is 'connected' only for networks; elsewhere it means 'on'.
PT_BR_NET = [('desligado', 'desconectado'), ('Desligado', 'Desconectado'), ('ligado', 'conectado'),
             ('Ligado', 'Conectado'), ('ligada', 'conectada'), ('Ligada', 'Conectada')]

def _words(text, pairs):
    for a, b in pairs:
        text = re.sub(r'(?<![\w-])'+re.escape(a)+r'(?![\w-])', b, text)
    return text

def br(text, en=''):
    text = _words(text, PT_BR)
    if re.search(r'onnect|Offline|Wi-Fi|Ethernet', en):
        text = _words(text, PT_BR_NET)
    for a, b in PT_BR_AFTER:
        text = text.replace(a, b)
    return text

def write(name, data):
    OUT.mkdir(parents=True, exist_ok=True)
    path = OUT/f'{name}.json'
    path.write_text(json.dumps(dict(sorted(data.items())), ensure_ascii=False, indent=1)+'\n', encoding='utf-8')
    print(f'{path.relative_to(HERE.parents[1])}: {len(data)} texts')

def check(lang, key, value):
    want = set(re.findall(r'\{\w+\}', key))
    if set(re.findall(r'\{\w+\}', value)) != want:
        raise SystemExit(f'{lang}: placeholders differ in {key!r} -> {value!r}')

def main():
    cats = {'pt': {}, 'id': {}, 'tet': {}, 'pt_BR': {}}
    seen = set()
    for row in FULL + NEW:
        en, pt, idn, tet = row
        tet = TETUN_FIX.get(en, tet)
        for a, b in TETUN_WORDS:
            tet = tet.replace(a, b)
        if en in seen:
            raise SystemExit(f'duplicate: {en!r}')
        seen.add(en)
        for lang, value in (('pt', pt), ('id', idn), ('tet', tet)):
            check(lang, en, value)
            if value != en: cats[lang][en] = value
        b = br(pt, en)
        if b != pt: cats['pt_BR'][en] = b
    for lang in LANGS: cats[lang] = {}
    seen = set()
    for row in CORE:
        en, values = row[0], row[1:]
        if len(values) != len(LANGS): raise SystemExit(f'wrong column count: {en!r}')
        if en in seen: raise SystemExit(f'duplicate: {en!r}')
        seen.add(en)
        for lang, value in zip(LANGS, values):
            check(lang, en, value)
            if value != en: cats[lang][en] = value
    for name, data in cats.items():
        write(name, data)

if __name__ == '__main__':
    main()
