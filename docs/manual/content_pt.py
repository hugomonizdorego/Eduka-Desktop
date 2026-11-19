# Guia do utilizador do Edukasaun Desktop Suite: português (PT).
# A mesma estrutura de content_en.py; os nomes da interface seguem a tradução
# portuguesa do Eduka-Desktop (as imagens mostram a interface em inglês).
HTML_LANG = 'pt'
FILE_SUFFIX = 'Portugues'
TITLE = 'Edukasaun Desktop Suite — Guia do Utilizador'
SUBTITLE = 'Versão {version} · Eduka-Desktop, Eduka-Panel, Eduka-Quick e Eduka-Settings'
COVER_META = ('O ambiente de trabalho do **Edukasaun OS**, feito para as escolas, sobre a sessão LXQt do Debian. '
              'Imagens: interface em inglês, tema Eduka-Pastel, ecrã de 1366 × 768. Versão {version}, novembro de 2026.')
FOOTER = 'Edukasaun Desktop Suite — Guia do Utilizador (Português)'
TOC_INTRO = ('Todas as partes do ambiente de trabalho: o menu iniciar, o painel, o Centro de ações, as definições e as novidades '
             'da versão 0.11 Pré-estável. As imagens mostram a interface em inglês; entre parênteses aparece o nome em inglês.')
LABELS = {'contents': 'Índice', 'tip': 'Dica', 'note': 'Nota', 'warn': 'Importante'}

SECTIONS = [
('intro', 'Bem-vindo ao Edukasaun Desktop', [
    ('p', 'O **Edukasaun Desktop Suite** é o ambiente de trabalho do Edukasaun OS. Foi pensado para as escolas: alunos, '
          'professores e secretarias têm um ambiente claro e simpático, que funciona tanto em portáteis novos como em computadores '
          'antigos. Funciona na sessão **LXQt** do Debian, por isso é leve e rápido; o LXQt fornece a sessão, o gestor de ficheiros '
          '(PCManFM-Qt), o terminal e muitas ferramentas, e o Eduka acrescenta o seu próprio menu iniciar, painel e definições.'),
    ('h3', 'As partes do conjunto'),
    ('table', ['Parte', 'O que faz'], [
        ['**Eduka-Desktop**', 'O menu iniciar: todos os programas por categorias, uma caixa de pesquisa, favoritos e informação do sistema.'],
        ['**Eduka-Panel**', 'A barra em baixo: botão MENU, barra de tarefas, áreas de trabalho, ícones de estado, notificações e relógio.'],
        ['**Centro de ações**', 'Abre a partir do relógio: calendário e agenda, interruptores rápidos, volume, brilho e botões da sessão.'],
        ['**Eduka-Quick**', 'Um lançador rápido redondo e transparente para os programas mais usados ([[Super+Q]]).'],
        ['**Eduka-Settings**', 'Uma janela para todas as definições: aspeto, painel, janelas, ecrã, som, teclado, rato, utilizadores e mais.'],
    ]),
    ('img', 'desktop', 'O ambiente de trabalho depois de entrar: ícones à esquerda, o Eduka-Panel em baixo.'),
    ('h3', 'Novidades da versão 0.11 Pré-estável'),
    ('ul', [
        'O Eduka-Desktop abre com um clique em MENU ou um toque em [[Super]], também com o Centro de ações aberto.',
        'A pesquisa do Eduka-Desktop também encontra as páginas do Eduka-Settings ("sound", "mouse", "workspace" …).',
        'Um tema predefinido em azul suave, nas cores do logótipo do Edukasaun OS.',
        'Uma página **Som** completa: dispositivos, testes, som nítido com o EasyEffects e correções para estalidos ou falta de som.',
        'Áreas de trabalho, cantos ativos, foco que segue o rato, colar com o botão do meio e histórico da área de transferência ([[Super+V]]).',
        'Gravação do ecrã com som ([[Super+Alt+R]]) e **Forçar fecho** para programas que deixam de responder.',
        'Vidro fosco, tocar e arrastar no touchpad, mesas digitalizadoras, a placa gráfica dedicada para jogos e efeitos Compiz opcionais.',
        'Melhor suporte para sessões Wayland (labwc, KWin) e uma lista dos dispositivos que ainda precisam de controlador.',
    ]),
    ('note', 'As imagens deste guia mostram a interface em inglês. O Eduka-Desktop também está traduzido em português, tétum e '
             'indonésio (Eduka-Settings → Idioma e hora).'),
]),
('login', 'Entrar e sair', [
    ('p', 'No ecrã de entrada escolha a sua conta (ou escreva o nome), escreva a palavra-passe e prima [[Enter]]. Os computadores com '
          'leitor de impressões digitais também aceitam um dedo, se isso foi ligado em Eduka-Settings → Entrada e impressão digital.'),
    ('p', 'O ecrã de entrada só oferece a sessão **Eduka-Desktop**; ela inicia o LXQt com o Eduka-Panel e o Eduka-Desktop. A primeira '
          'entrada de uma conta nova configura o fundo, o tema, o teclado e a escala de ecrã recomendada.'),
    ('h3', 'O ecrã de saída'),
    ('p', 'Prima [[Ctrl+Alt+Delete]], ou use os botões em baixo no Centro de ações, para abrir o ecrã de saída. Um clique executa logo a '
          'ação: **Bloquear** (os programas ficam abertos e a sua palavra-passe desbloqueia o ecrã), **Terminar sessão**, **Suspender**, '
          '**Hibernar** (quando o computador o permite), **Reiniciar** ou **Desligar**. [[Esc]] fecha o ecrã sem fazer nada.'),
    ('img', 'leave', 'O ecrã de saída com o ambiente de trabalho desfocado por trás.'),
    ('tip', 'Guarde o seu trabalho antes de terminar a sessão, reiniciar ou desligar. [[Super+L]] bloqueia o ecrã rapidamente quando sai do computador.'),
]),
('menu', 'Eduka-Desktop: o menu iniciar', [
    ('p', 'Clique em **MENU**, à esquerda no painel, ou prima a tecla [[Super]] (a tecla com o logótipo do Windows), para abrir o '
          'Eduka-Desktop. Clique outra vez em MENU, prima outra vez [[Super]] ou prima [[Esc]] para o fechar. O menu também abre com um '
          'só clique quando o Centro de ações ou outra janela do painel está aberta.'),
    ('img', 'menu', 'O Eduka-Desktop com a categoria Tudo (All) na vista Grelha.'),
    ('h3', 'Categorias'),
    ('p', 'A coluna da esquerda lista as categorias. **Edukasaun** reúne os programas para aprender, ciência e jogos; as outras seguem '
          'os grupos habituais: Acessórios, Gráficos, Internet, Escritório, Programação, Som e vídeo, Ferramentas do sistema, Acesso '
          'universal e Preferências. **Tudo** mostra todos os programas. As categorias vazias ficam escondidas.'),
    ('h3', 'Pesquisa'),
    ('p', 'Com o menu aberto, comece simplesmente a escrever. A pesquisa procura em todos os programas, seja qual for a categoria '
          'escolhida, e entende nomes, descrições e palavras-chave. [[Enter]] inicia o primeiro resultado. A partir da versão 0.11 '
          'Pré-estável a pesquisa também mostra as **páginas do Eduka-Settings** correspondentes: escreva "sound", "mouse" ou '
          '"workspace" (ou as palavras na sua língua) e abra a definição diretamente.'),
    ('img', 'menu-search', 'Pesquisa de "sound": as páginas correspondentes do Eduka-Settings.'),
    ('h3', 'Grelha, Lista e favoritos'),
    ('ul', [
        '**Grelha** mostra mosaicos grandes; **Lista** mostra os nomes com uma descrição curta (boa para leitores de ecrã e ecrãs pequenos).',
        'A coluna **Favoritos**, à direita, guarda os programas que usa mais. Clique com o botão direito num programa → **Adicionar aos favoritos**.',
        '**Informação do sistema** mostra a versão do Edukasaun OS e do ambiente de trabalho.',
        'Os botões em baixo abrem o Gestor de ficheiros, o Terminal, o Eduka-Settings e o Sobre.',
        'Em ecrãs pequenos (menos de 900 píxeis de largura) o menu usa um formato mais estreito e mostra os favoritos como uma categoria.',
    ]),
    ('h3', 'O menu do botão direito de um programa'),
    ('ul', [
        '**Abrir** inicia o programa; **Executar com a placa gráfica dedicada** aparece em portáteis com duas placas gráficas.',
        '**Adicionar aos favoritos**, **Adicionar ao ambiente de trabalho** (um ícone no ambiente de trabalho) e **Fixar na barra de tarefas** (um botão no painel).',
        '**Adicionar ao Eduka-Quick** coloca o programa no lançador rápido redondo.',
        '**Abrir a pasta** mostra onde está o ficheiro do programa.',
    ]),
]),
('panel', 'Eduka-Panel', [
    ('p', 'O Eduka-Panel é a barra em baixo no ecrã. Da esquerda para a direita mostra o botão MENU, os programas fixados, as janelas '
          'abertas (a barra de tarefas), as áreas de trabalho, os ícones de estado e o relógio.'),
    ('h3', 'Barra de tarefas'),
    ('p', 'Cada janela aberta tem um botão. Um clique mostra a janela, um segundo clique minimiza-a. Com várias áreas de trabalho, a barra '
          'de tarefas mostra as janelas da área atual. Clique com o botão direito no botão de uma janela para mais opções:'),
    ('ul', [
        '**Ativar**, **Minimizar**, **Maximizar** ou **Restaurar**, e **Fechar**.',
        '**Adicionar aos favoritos** e **Fixar na barra de tarefas** (o programa mantém o botão quando é fechado).',
        '**Forçar fecho**: fecha um programa de imediato, também quando já não responde (ver o capítulo "Programas que deixam de responder").',
    ]),
    ('img', 'task-menu', 'O menu do botão direito de uma janela na barra de tarefas.', 'half'),
    ('h3', 'Áreas de trabalho'),
    ('p', 'Os números **1 2 3 4** são as áreas de trabalho virtuais: ambientes separados para tarefas diferentes, por exemplo uma aula na '
          'área 1 e o navegador na área 2. Clique num número, deslize sobre os números ou prima [[Ctrl+Super+Left]] e '
          '[[Ctrl+Super+Right]]. O número de áreas de trabalho define-se em Eduka-Settings → Janelas e áreas de trabalho.'),
    ('h3', 'Ícones de estado'),
    ('table', ['Ícone', 'Clique', 'Botão direito ou mais'], [
        ['Unidades amovíveis', 'Lista as pens USB e cartões; ejete-os em segurança.', 'Abrir a unidade no gestor de ficheiros.'],
        ['Rede', 'Redes Wi-Fi e ligação por cabo.', 'Definições de rede.'],
        ['Bluetooth', 'Ligar ou desligar, emparelhar um dispositivo (só quando o computador tem Bluetooth).', 'Gestor de Bluetooth.'],
        ['Som', 'Volume, dispositivo de saída e o interruptor Som nítido.', 'Deslize para mudar o volume.'],
        ['Bateria', 'Carga, tempo restante e modo de energia (portáteis).', 'Definições de energia.'],
        ['Notificações', 'As últimas mensagens; Não incomodar.', 'Definições de notificações.'],
        ['Teclado (US, PT …)', 'Muda a disposição do teclado.', 'Definições do teclado.'],
        ['Relógio', 'Abre o Centro de ações.', 'Estilo e definições do relógio.'],
    ]),
    ('img', 'sound-popup', 'A janela do som: volume, saída, Som nítido e definições de som.', 'half'),
    ('tip', 'Enquanto o ecrã é gravado aparece no painel um pequeno botão vermelho **REC**; clique nele para parar.'),
    ('h3', 'Posição e aspeto do painel'),
    ('p', 'Clique com o botão direito numa parte vazia do painel para o mudar para outro lado do ecrã, para mudar as pontas (ovais, '
          'arredondadas ou quadradas) e para abrir as definições do painel. O Eduka-Panel mantém o seu lugar por cima das janelas '
          'maximizadas; só os programas em ecrã inteiro (vídeos, jogos, apresentações) o tapam.'),
]),
('action-center', 'O Centro de ações', [
    ('p', 'Clique no relógio do painel (ou prima [[Super+A]]) para abrir o Centro de ações. Clique outra vez no relógio, prima [[Esc]] '
          'ou clique fora para o fechar.'),
    ('img', 'action-center', 'O Centro de ações (Action Center).', 'half'),
    ('ul', [
        '**Cartão do relógio**: a hora, uma saudação e a data, com o tempo de hoje. Clique nele para o globo e os fusos horários; '
        'clique com o botão direito para o estilo do relógio (digital, analógico, com segundos …).',
        '**Sincronizar a hora** (em cima à esquerda): acerta o relógio e o fuso horário pela internet.',
        '**Mosaicos**: Rede, Bluetooth, Modo avião, Ecrã (modos do projetor), Não incomodar e Definições. Clique com o botão direito '
        'num mosaico para abrir as suas definições.',
        '**Música e vídeo**: enquanto um programa toca, aparecem em cima anterior, reproduzir/pausa e seguinte.',
        '**Calendário e agenda**: escolha um dia e prima **+ Agenda** para escrever uma nota ou um lembrete com hora.',
        'Barras de **volume e brilho**; a seta ao lado do volume escolhe o dispositivo de saída.',
        '**Bloquear, Terminar sessão, Reiniciar, Desligar** em baixo.',
        'A pega em cima torna o Centro de ações maior ou menor; a seta em cima à direita liga o modo compacto.',
    ]),
]),
('quick', 'Eduka-Quick', [
    ('p', 'Prima [[Super+Q]] para abrir o Eduka-Quick onde está o ponteiro do rato. Mostra num círculo os programas que usa mais. '
          'Aponte para uma fatia e clique, ou prima o número que ela mostra ([[1]] a [[9]]). [[Esc]] fecha-o.'),
    ('img', 'quick', 'O Eduka-Quick, o lançador rápido redondo.', 'half'),
    ('ul', [
        'Mantenha o botão do rato premido no centro transparente e arraste para mover o Eduka-Quick; da próxima vez abre aí.',
        'Clique com o botão direito num programa no Eduka-Desktop → **Adicionar ao Eduka-Quick** para o acrescentar.',
        'Eduka-Settings → Eduka-Quick escolhe o número de fatias (4 a 12), o aspeto e os programas.',
    ]),
]),
('notifications', 'Notificações', [
    ('p', 'Os programas mostram mensagens curtas em baixo à direita, por cima do relógio. Desaparecem sozinhas passados alguns '
          'segundos; o ícone das notificações no painel guarda as últimas. Clique nele para as ler outra vez ou para as apagar.'),
    ('img', 'recording-saved', 'Uma notificação: a gravação do ecrã foi guardada.', 'half'),
    ('p', '**Não incomodar** (no Centro de ações e na lista de notificações) deixa as mensagens em silêncio; só as urgentes continuam a '
          'aparecer. Eduka-Settings → Eduka-Panel → Notificações define quanto tempo as mensagens ficam e se são guardadas.'),
]),
('settings', 'Eduka-Settings', [
    ('p', 'Abra o Eduka-Settings a partir do menu (botão **Definições**), com [[Super+I]] ou com o botão direito num mosaico do Centro de '
          'ações. A primeira página, **Todas as definições**, mostra todas as definições por grupos, com a sua própria caixa de '
          'pesquisa. A lista à esquerda leva às páginas; as páginas sobre o mesmo assunto partilham uma entrada com separadores em cima.'),
    ('img', 'settings-overview', 'Todas as definições (All Settings), a primeira página do Eduka-Settings.'),
    ('p', 'A maior parte das alterações é usada logo. **Aplicar** ([[Ctrl+S]]) aplica tudo e mantém a janela aberta; **Guardar e fechar** '
          'aplica e fecha. As definições do computador inteiro (outras contas, ecrã de entrada, Controlo parental, impressões '
          'digitais) pedem a palavra-passe de um administrador. **Repor predefinições**, em baixo à esquerda, repõe as predefinições '
          'Edukasaun do Eduka-Desktop e do Eduka-Panel (tema, transparência, tamanho, disposição, botão do menu); os favoritos, os '
          'programas fixados e o ecrã de entrada mantêm-se.'),
    ('table', ['Grupo', 'Páginas'], [
        ['PERSONALIZAR', 'Aparência (Tema, Tipos de letra, Efeitos) · Fundo e ícones'],
        ['AMBIENTE', 'Eduka-Desktop · Eduka-Quick · Eduka-Panel (Painel, Relógio, Notificações) · Janelas e áreas de trabalho'],
        ['DISPOSITIVOS', 'Ecrã · Som (Som, Som nítido, Qualidade e correções) · Teclado (Teclado, Atalhos) · Rato e toque'],
        ['SISTEMA', 'Utilizadores · Idioma e hora · Acessibilidade · Controlo parental · Entrada e impressão digital · Manutenção'],
    ]),
]),
('look', 'Aparência, fundo e tipos de letra', [
    ('p', '**Aparência → Tema** escolhe um de sete temas. Cada tema também dá estilo aos programas GTK e Qt e às molduras das janelas.'),
    ('table', ['Tema', 'Para'], [
        ['**Eduka-Pastel** (predefinido)', 'O azul suave do logótipo do Edukasaun OS; claro e amigável para a escola.'],
        ['Eduka-Default-Theme', 'Um aspeto calmo e claro com destaques coloridos.'],
        ['**Eduka-Low-Theme**', 'Computadores muito antigos ou lentos: sem transparência, sem efeitos, a menor memória.'],
        ['Liquid Glass', 'Vidro leitoso com contornos claros (precisa de compositor e de 4 GB de memória).'],
        ['Edukasaun-Dark', 'Um tema escuro para a noite ou salas com projetores.'],
        ['Eduka-Transparan', 'Painéis e menus transparentes.'],
        ['Eduka-MultiColor', 'Uma cor diferente para cada categoria, mosaico e botão do painel.'],
    ]),
    ('img', 'settings-appearance', 'Aparência → Tema.'),
    ('ul', [
        '**Cor de destaque**: a cor dos botões, interruptores e destaques.',
        '**Vidro fosco**: um desfoque atrás do Eduka-Panel, do Eduka-Desktop e das suas janelas (precisa de gráficos 3D; desligado no VirtualBox).',
        '**Ambiente de trabalho desfocado atrás do ecrã de saída**: funciona em qualquer computador.',
        '**Tipos de letra**: as letras do ambiente de trabalho, dos documentos e dos títulos das janelas, o tamanho e a suavização.',
        '**Efeitos**: animações e o compositor (Automático serve para a maioria dos computadores).',
        '**Fundo e ícones**: imagens de /usr/share/background/Edukasaun ou suas, uma apresentação de imagens, e os ícones do ambiente de trabalho.',
    ]),
]),
('desktop-panel', 'Definições do Eduka-Desktop, Eduka-Quick e Eduka-Panel', [
    ('p', '**Eduka-Desktop**: o tamanho do menu, Grelha ou Lista, as categorias mostradas, as cores dos mosaicos e as ajudas de acessibilidade.'),
    ('img', 'settings-desktop', 'Eduka-Settings → Eduka-Desktop.'),
    ('p', '**Eduka-Panel → Painel**: a altura e a posição do painel, o texto do botão MENU, os programas fixados e a barra de tarefas. '
          '**Relógio**: relógio digital ou analógico, segundos, a data e o tempo. **Notificações**: quanto tempo ficam as mensagens, '
          'Não incomodar e o histórico.'),
    ('img', 'settings-panel', 'Eduka-Settings → Eduka-Panel → Painel.'),
]),
('windows', 'Janelas, áreas de trabalho e captura do ecrã', [
    ('p', '**Janelas e áreas de trabalho** tem três separadores.'),
    ('h3', 'Janelas'),
    ('ul', [
        '**Foco**: "Clique numa janela para trabalhar nela" (como no Windows), ou "a janela debaixo do ponteiro recebe o teclado" '
        '(o foco segue o rato; a janela não sobe).',
        '**Colar com o botão do meio**: selecione texto e clique com o botão do meio do rato (ou toque com três dedos) para o colar.',
        '**Histórico da área de transferência**: [[Super+V]] lista os textos que copiou. Fica só na memória, nunca no disco; as '
        'palavras-passe copiadas de um gestor de palavras-passe não são guardadas.',
        '**Programas que não respondem**: propor forçar o fecho de um programa que não responde há 1, 2 ou 5 minutos.',
        '**Gestor de janelas**: xfwm4 (recomendado), Openbox (o mais leve), KWin, Marco ou Compiz (efeitos 3D, instalado à parte). '
        'A escolha é usada a partir da próxima entrada.',
    ]),
    ('img', 'settings-windows', 'Janelas e áreas de trabalho → Janelas.'),
    ('img', 'clipboard', 'O histórico da área de transferência ([[Super+V]]): clique num texto para o copiar outra vez.', 'half'),
    ('h3', 'Áreas de trabalho e cantos'),
    ('p', 'Escolha o número de áreas de trabalho (1 a 8), se o painel as mostra e se a barra de tarefas mostra só as janelas da área '
          'atual. **Cantos ativos**: empurre o ponteiro para um canto do ecrã para abrir o Eduka-Desktop, mostrar o ambiente de '
          'trabalho, abrir o Centro de ações ou o Eduka-Quick, mudar de área de trabalho, mostrar as notificações ou bloquear o ecrã. '
          'Nada acontece enquanto um botão do rato estiver premido. Os cantos ativos funcionam na sessão X11.'),
    ('img', 'settings-workspaces', 'Janelas e áreas de trabalho → Áreas de trabalho e cantos.'),
    ('h3', 'Capturas e gravação'),
    ('ul', [
        '[[Print]]: o ecrã inteiro · [[Alt+Print]]: a janela ativa · [[Super+Shift+S]]: uma parte do ecrã · [[Super+Print]]: '
        'guardada logo em Imagens/Screenshots.',
        '[[Super+Alt+R]] inicia uma **gravação do ecrã** e para-a outra vez; o botão vermelho REC do painel também a para.',
        'É gravado o som do computador e, se quiser, o microfone. Os vídeos são ficheiros MP4 em Vídeos/Screen recordings; tocam em '
        'qualquer computador e telemóvel.',
        '"Fluidez" (15, 25 ou 30 imagens por segundo) e "Tamanho" (ficheiro pequeno até melhor imagem) servem computadores antigos e novos.',
    ]),
    ('img', 'recording', 'Durante a gravação: o botão vermelho REC com o tempo no Eduka-Panel.'),
    ('img', 'settings-capture', 'Janelas e áreas de trabalho → Capturas e gravação.'),
]),
('hang', 'Programas que deixam de responder', [
    ('p', 'Por vezes um programa bloqueia: a janela fica, mas já não reage. O Eduka-Panel dá por isso. Quando um programa não responde '
          'há dois minutos (o tempo pode ser mudado), uma pequena janela pergunta o que fazer:'),
    ('img', 'hang-dialog', 'Um programa não está a responder: Esperar ou Forçar fecho.', 'half'),
    ('ul', [
        '**Esperar**: o programa recebe mais tempo; muitos programas voltam a responder depois de uma tarefa longa.',
        '**Forçar fecho**: o programa é fechado de imediato. O trabalho não guardado nesse programa perde-se.',
    ]),
    ('p', 'Também pode fechar um programa bloqueado: prima [[Ctrl+Alt+Esc]] para a janela ativa, ou clique com o botão direito no seu '
          'botão da barra de tarefas → **Forçar fecho**. O Eduka pergunta primeiro. Os programas que mantêm o ambiente de trabalho a '
          'funcionar (o painel, o gestor de janelas, os ícones do ambiente de trabalho) nunca são fechados.'),
    ('img', 'force-close', 'Forçar fecho depois de [[Ctrl+Alt+Esc]].', 'half'),
]),
('display', 'Ecrã e gráficos', [
    ('p', 'A página **Ecrã** mostra que tipo de computador o Eduka-Desktop encontrou (portátil, computador de secretária, tablet ou '
          'máquina virtual) e o tamanho do ecrã.'),
    ('ul', [
        '**Escala** (75 a 200 %): torna o texto, os ícones, os painéis e as janelas maiores ou mais pequenos ao mesmo tempo. A escala '
        'recomendada está marcada. A nova escala é usada depois de terminar a sessão e voltar a entrar.',
        '**Ecrãs e resolução**: organizar dois monitores ou um projetor (definições de monitores do LXQt). [[Super+P]] muda o modo do projetor.',
        '**Gráficos**: as placas gráficas e os seus controladores, com conselhos quando falta um controlador ou o seu firmware. Em '
        'portáteis com duas placas, os jogos e programas que o pedem iniciam na placa dedicada; qualquer programa pode ser iniciado '
        'nela a partir do seu menu do botão direito no Eduka-Desktop.',
    ]),
    ('img', 'settings-display', 'Ecrã: o tipo de computador e a escala.'),
]),
('sound', 'Som', [
    ('p', 'Os problemas de som são frequentes nos computadores com Linux, por isso o Eduka-Settings tem uma página **Som** completa com '
          'três separadores. Funciona com PipeWire e com PulseAudio.'),
    ('h3', 'Som'),
    ('ul', [
        '**Altifalantes e auscultadores**: escolha a saída (altifalantes integrados, auscultadores, HDMI para projetor ou televisor, '
        'Bluetooth, USB) e a ligação; ajuste o volume; **Testar esquerda**, **Testar ambos** e **Testar direita** tocam um som curto em cada lado.',
        '"Permitir mais alto do que 100%" ajuda os altifalantes fracos dos portáteis (o som pode distorcer).',
        '**Microfone**: o dispositivo de entrada, a ligação e o nível.',
        '**Placa de som**: o perfil de cada placa. Um perfil com HDMI envia o som para um projetor; para auscultadores Bluetooth '
        '"High Fidelity Playback (A2DP)" soa melhor, "Headset" é para chamadas com o microfone.',
    ]),
    ('img', 'settings-sound', 'Som: dispositivos, volume e testes.'),
    ('h3', 'Som nítido'),
    ('p', 'O **EasyEffects** melhora o som de todos os programas. É um programa à parte: prima uma vez **Instalar o EasyEffects…** e '
          'depois escolha um som. Para altifalantes e auscultadores: Desligado, **Voz nítida** (aulas, vídeos e chamadas), Música, '
          'Volume uniforme, Altifalantes de portátil, Loudness, Auscultadores e Graves (os quatro últimos são predefinições de '
          'JackHack96). Para o microfone: **Microfone nítido** (menos ruído de fundo para aulas online e gravações). O interruptor '
          '"Som nítido" na janela do som do painel liga-o ou desliga-o rapidamente.'),
    ('img', 'settings-clear-sound', 'Som nítido com o EasyEffects.'),
    ('h3', 'Qualidade e correções'),
    ('ul', [
        '**Tocar a música à sua própria taxa** (44,1 ou 48 kHz) em vez de a converter.',
        '**Manter a placa de som acordada**: sem cortar o primeiro segundo e sem estalos; os projetores mantêm o som.',
        '**Memória de som maior**: sem estalidos em computadores antigos ou ocupados (um pouco de atraso).',
        '**Melhor qualidade de conversão** (usa mais tempo do processador).',
        '**Aplicar e reiniciar o som** usa as escolhas; **Repor as definições de som** retira-as outra vez.',
        '**Verificar o meu som** procura os problemas habituais (sem som, volume muito baixo, sem dispositivo, Bluetooth em modo de '
        'chamada, firmware em falta) e propõe uma correção com um clique para cada um.',
    ]),
    ('img', 'settings-sound-quality', 'Qualidade e correções com o resultado de "Verificar o meu som".'),
    ('tip', 'O projetor não tem som? Escolha a saída HDMI no separador Som, ou o perfil HDMI da placa, e prima "Testar ambos".'),
]),
('keyboard', 'Teclado e atalhos', [
    ('p', '**Teclado**: as disposições (por exemplo US, português, indonésio), a tecla que muda entre elas, a repetição das teclas e o '
          'Num Lock ("Automático" liga-o nos computadores de secretária e desliga-o nos portáteis). O painel mostra a disposição atual.'),
    ('img', 'settings-keyboard', 'Teclado.'),
    ('p', '**Atalhos** lista todos os atalhos do LXQt e do Eduka juntos. Desmarque uma linha para libertar a sua tecla. Uma tecla que o '
          'LXQt, o utilizador ou o gestor de janelas já usam nunca recebe uma segunda função.'),
    ('table', ['Teclas', 'O que fazem'], [
        ['[[Super]]', 'Abrir ou fechar o Eduka-Desktop'],
        ['[[Super+Q]]', 'Eduka-Quick'],
        ['[[Super+S]]', 'Procurar programas e ficheiros'],
        ['[[Super+R]] ou [[Alt+F2]]', 'Executar um comando'],
        ['[[Super+V]]', 'Histórico da área de transferência'],
        ['[[Super+E]]', 'Gestor de ficheiros'],
        ['[[Super+I]]', 'Eduka-Settings'],
        ['[[Super+A]]', 'Centro de ações'],
        ['[[Super+N]]', 'Notificações'],
        ['[[Super+D]]', 'Mostrar o ambiente de trabalho (outra vez: as janelas voltam)'],
        ['[[Super+M]] / [[Super+Shift+M]]', 'Minimizar todas as janelas / trazê-las de volta'],
        ['[[Super+Up]] / [[Super+Down]]', 'Maximizar / restaurar a janela'],
        ['[[Super+Left]] / [[Super+Right]]', 'Janela na metade esquerda / direita do ecrã'],
        ['[[Super+Shift+Left]] / [[Super+Shift+Right]]', 'Janela para o ecrã da esquerda / direita'],
        ['[[Ctrl+Super+Left]] / [[Ctrl+Super+Right]]', 'Área de trabalho anterior / seguinte'],
        ['[[Alt+Tab]]', 'Mudar de janela'],
        ['[[Alt+F4]]', 'Fechar a janela'],
        ['[[Ctrl+Alt+Esc]]', 'Forçar o fecho do programa da janela ativa'],
        ['[[Ctrl+Shift+Esc]]', 'Gestor de tarefas'],
        ['[[Ctrl+Alt+T]]', 'Terminal'],
        ['[[Super+L]]', 'Bloquear o ecrã'],
        ['[[Ctrl+Alt+Delete]]', 'Ecrã de saída: bloquear, terminar sessão, suspender, reiniciar, desligar'],
        ['[[Print]] / [[Alt+Print]]', 'Captura do ecrã / da janela'],
        ['[[Super+Shift+S]]', 'Captura de uma área'],
        ['[[Super+Print]]', 'Captura guardada logo'],
        ['[[Super+Alt+R]]', 'Iniciar ou parar uma gravação do ecrã'],
        ['[[Super+P]]', 'Ecrãs e projetor'],
        ['[[Super+.]]', 'Emoji e símbolos'],
        ['[[Super+Space]]', 'Disposição de teclado seguinte'],
        ['[[Super+U]]', 'Definições de acessibilidade'],
        ['[[Ctrl+Super+Enter]]', 'Leitor de ecrã ligado ou desligado'],
        ['[[Ctrl+Super+O]]', 'Teclado no ecrã ligado ou desligado'],
        ['[[Super+=]]', 'Lupa'],
    ]),
    ('img', 'settings-shortcuts', 'Teclado → Atalhos.'),
]),
('mouse', 'Rato, touchpad, ecrã tátil e caneta', [
    ('ul', [
        '**Rato**: velocidade do ponteiro, botões para canhotos, velocidade do duplo clique e a roda.',
        '**Touchpad**: ligado ou desligado, tocar para clicar (um dedo esquerdo, dois dedos direito), deslocamento natural, desligar '
        'ao escrever, **tocar e arrastar** (toque, volte a pousar o dedo e mova-o) e **bloqueio de arrasto** (levantar o dedo não '
        'larga o que arrasta; toque para largar). As definições feitas sem touchpad ficam guardadas para quando houver um.',
        '**Ecrã tátil**: o ecrã a que o toque pertence, a rotação, o deslocamento suave com o dedo, os gestos com três e quatro dedos '
        'e o teclado no ecrã.',
        '**Mesa digitalizadora** (separador Ecrã tátil): com um projetor ou um segundo monitor a caneta desenha num só ecrã, para que '
        'os círculos fiquem redondos.',
    ]),
    ('img', 'settings-touchpad', 'Rato e toque → Touchpad com tocar e arrastar.'),
    ('img', 'settings-touchscreen', 'Rato e toque → Ecrã tátil e mesa digitalizadora.'),
]),
('system', 'Utilizadores, idioma, acessibilidade e controlo parental', [
    ('h3', 'Utilizadores'),
    ('p', 'Acrescente e remova contas, mude nomes, palavras-passe e imagens, e escolha quem é administrador. Faça uma conta por '
          'professor (Administrador) e por aluno ou turma (Normal). Mantenha pelo menos duas contas de administrador na escola.'),
    ('img', 'settings-users', 'Utilizadores.'),
    ('h3', 'Idioma e hora'),
    ('p', '**Idioma e arranque**: a língua do Eduka-Desktop e dos outros programas (tétum, português, inglês, indonésio …) e os '
          'programas que iniciam depois da entrada. **Data e hora**: o fuso horário, a hora pela rede e o relógio.'),
    ('h3', 'Acessibilidade'),
    ('ul', [
        '**Visão**: contraste forte, texto grande, um ponteiro maior, menos movimento, a lupa e o teclado no ecrã.',
        '**Audição**: o estado da rede, do som e dos alertas como texto no Eduka-Panel, e som mono (os dois ouvidos e os dois altifalantes tocam tudo).',
        '**Leitor de ecrã**: o Orca lê o ecrã em voz alta; escolha e experimente a voz.',
    ]),
    ('img', 'settings-accessibility', 'Acessibilidade → Visão.'),
    ('h3', 'Controlo parental e privacidade'),
    ('p', 'O Controlo parental define um limite de tempo para este computador e o tempo permitido, com recomendações por idade '
          '(crianças pequenas, escola primária, adolescentes, uma aula de informática, trabalhos de casa). O Eduka-Panel mostra um '
          'lembrete amigável para descansar os olhos e mexer-se, também sem limite de tempo, e uma mensagem antes de o computador se '
          'desligar. As alterações pedem a palavra-passe de um administrador. **Privacidade** apaga os ficheiros recentes, as '
          'miniaturas e o lixo.'),
    ('img', 'settings-parental', 'Controlo parental.'),
    ('h3', 'Entrada e impressão digital'),
    ('p', 'O aspeto do ecrã de entrada (SDDM, ou LightDM como opção), a entrada automática (pede sempre a palavra-passe de um '
          'administrador) e a entrada com impressão digital: acrescente um dedo e depois ligue "Usar a impressão digital".'),
]),
('maintenance', 'Manutenção, memória, controladores e firmware', [
    ('ul', [
        '**Reconstruir a lista de aplicações**: depois de instalar ou remover programas.',
        '**Recarregar o Eduka-Desktop** e **Reiniciar o Eduka-Panel**: quando o menu ou o painel parecem errados ou deixam de responder.',
        '**Reparar o tema e a sessão do LXQt**: quando o LXQt pede um gestor de janelas ou o tema parece errado; as definições antigas ficam guardadas como cópia.',
        '**Controladores e firmware**: lista os dispositivos Wi-Fi, de rede, de som, gráficos e Bluetooth que ainda não têm '
        'controlador, com o pacote de firmware a instalar ("Instalar o firmware em falta…"). Reinicie o computador depois.',
        '**Memória**: poupança de memória, um aviso antes de a memória acabar, os programas que usam mais memória, e o zram e o '
        'earlyoom, que mantêm fluidos os computadores com 2 a 4 GB de memória.',
    ]),
    ('img', 'settings-maintenance', 'Manutenção com Controladores e firmware.'),
]),
('old-pc', 'Computadores antigos, Wayland e Compiz', [
    ('h3', 'Computadores antigos e lentos'),
    ('ul', [
        'Escolha o **Eduka-Low-Theme** (Aparência → Tema): sem transparência e sem efeitos.',
        'Use o **Openbox** como gestor de janelas (Janelas e áreas de trabalho → Janelas) e deixe o compositor em Automático.',
        'Ligue o zram e o earlyoom (Manutenção → Memória); deixe o Som nítido desligado em computadores com 2 GB de memória.',
        'Grave o ecrã com "15 imagens por segundo" e "Ficheiro pequeno".',
    ]),
    ('h3', 'Wayland'),
    ('p', 'A sessão habitual na escola é X11. A sessão Wayland do LXQt é para testes: o Eduka-Desktop e o Eduka-Panel funcionam aí '
          'através do XWayland, e o Eduka-Settings também escreve as definições do touchpad, do rato, do teclado, do foco, do botão '
          'do meio e das áreas de trabalho no compositor Wayland (labwc ou KWin). Os cantos ativos e o Forçar fecho automático só '
          'funcionam em X11.'),
    ('h3', 'Compiz'),
    ('p', 'O Compiz acrescenta efeitos 3D (janelas ondulantes, o cubo, [[Super+W]] mostra todas as janelas lado a lado). É instalado à '
          'parte ("Instalar o Compiz (efeitos 3D)…" na página Janelas) e precisa de verdadeiros gráficos 3D. Se o Compiz não puder '
          'iniciar, o xfwm4 ou o Openbox assumem sozinhos, por isso as janelas têm sempre molduras.'),
]),
('help', 'Problemas e ajuda', [
    ('table', ['Problema', 'O que fazer'], [
        ['Sem som', 'Som → escolha a saída certa e prima "Testar ambos"; Qualidade e correções → "Verificar o meu som".'],
        ['Som com estalidos', 'Qualidade e correções → "Memória de som maior" e "Manter a placa de som acordada", depois "Aplicar e reiniciar o som".'],
        ['O projetor não tem som', 'Escolha a saída HDMI ou o perfil HDMI da placa.'],
        ['O Wi-Fi não funciona', 'Manutenção → Controladores e firmware: instale o firmware indicado e reinicie.'],
        ['Um programa bloqueou', 'Espere, ou [[Ctrl+Alt+Esc]] → Forçar fecho.'],
        ['O menu ou o painel parecem errados', 'Manutenção → Recarregar o Eduka-Desktop / Reiniciar o Eduka-Panel.'],
        ['Está tudo pequeno ou grande demais', 'Ecrã → Escala, depois termine a sessão e volte a entrar.'],
        ['O computador está lento', 'Eduka-Low-Theme, Openbox, zram e earlyoom (capítulo "Computadores antigos").'],
        ['Esqueceu a palavra-passe', 'Um administrador muda-a em Utilizadores; com a entrada por impressão digital pode definir uma nova depois de entrar com o dedo.'],
    ]),
    ('p', 'Sobre o Edukasaun Desktop (menu → Sobre, ou Manutenção → Sobre) mostra a versão e os créditos dos projetos que o Edukasaun '
          'Desktop usa. Sítio web: www.edukasaunos.tl.'),
    ('img', 'about', 'Sobre o Edukasaun Desktop.', 'half'),
]),
]
