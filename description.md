# Descrição do sistema Gerenciador de Programas

## Ícone do sistema

![Ícone do sistema](src/assets/icon/icon.ico)

## Programa

Sistema de gerenciamento de programas para fácil instalação ou desinstalação numa possível formatação ou configuração de computador ou numa otimização.

### FRONT-END Programa

#### Program Language

EN-US

#### Primeira tela

Conterá o título variável do programas, que varia de acordo com o Sistema Operacional.

Container onde aparecerá cada classe de função em forma de checklist.

No canto inferior esquerdo terá um botão que ao clicar seleciona ou desmarca todas as opções do container principal.

No canto inferior direito, haverá um botão de "Next", que ao clicar nele o sistema fechará a primeira tela e abrirá a segunda tela, e o sistema transmitirá um array somente com os dados das opções selecionadas.

#### Segunda tela

##### Container principal

Quando for aberta a segunda tela, o sistema irá mostrará os dados do array _data_ que está dentro de cada object do array _json_data_, e mostrará esses dados no container principal.

##### Menu suspenso

Cada opção é referente à variável _name_ dentro do object no array _json_data_ recebido do sistema de leitura de JSON, e ao clicar numa opção específica, o programa mostrará os dados do JSON referente, organizado em ordem alfabética no container de conteúdo.

##### Conteúdo

Será mostrado um checklist dos dados do JSON referente à opção seleciona no menu suspenso, com as seguintes características:

- Primeira coluna terá o checkbox;
- Segunda coluna terá o nome da função;
- Terceira coluna terá o tipo da função, se é _install_, _uninstall_ ou _function_.

##### Container de Botões

No canto inferior esquerdo, haverá um container com dois botões:

- Na direita, terá um botão de _Add Program_. Quando clicado, ele abre a tela 3.1 com as seguintes características:
  - No topo terá uma barra de pesquisa e um botão de _Search_;
  - Quando o usuário digitar algo na barra e clicar em _Search_ ou apertar enter, o sistema rodará uma função do backend que retorna um objeto com os programas relacionados encontrados;
  - No container principal será mostrado os dados desse objeto, mas em três colunas:
  - A primeira será um botão, que alterna entre _Add_ e _Remove_ dependendo do click do usuário;
  - Na segunda coluna será mostrado o nome do programa;
  - Na terceira coluna será mostrado o id do programa;

- Na esquerda do container, terá outro botão chamado _Remove Programs_, que quando clicado fará:
  - Abrirá a tela 3.2 com layout semelhante a 3.1;

##### Botão de execução

No canto inferior direito da tela 2, haverá um botão de _RUN_, que fechará a tela e dará início ao sistema principal em segundo plano.

### BACK-END Programa

#### JSON

##### Escrita em JSON

Quando for chamada função de geração de JSONs, o sistema verificará se o arquivo `user.json` existe no caminho `C:\Users\<user>\Downloads\Programs Manager`. Se não existir, ele cria o arquivo e insere a seguinte estrutura:

```json
{
  "name": "User",
  "description": "User data generated after execution of write system",
  "data": []
}
```

##### Leitura de JSON

###### JSON Interno

A leitura do JSON interno funciona praticamente igual ao sistema de [Escrita em JSON](#escrita-em-json), a diferença é que ao invés de escrever, esse sistema irá somente ler o arquivo e salvará os dados desse arquivo no array _json_data_.

###### JSON Externo

A leitura de JSON externo utilizará o Github RAW no link `https://raw.githubusercontent.com/JLBBARCO/programs-manager/main/program/system/<sistema_operacional>/json/<nome_do_arquivo>.json` e salvará os dados de cada JSON lido no array _json_data_.

#### log.log

Ao escrever no log.log, o sistema terá quatro tópicos de mensagens:

- \[INFO\]
- \[WARNING\]
- \[ERROR\]

O tópico _INFO_ será para informar que tal coisa começou ou aconteceu. Exemplos: `Start system`, `Find and read essentials.json`, `End system`.

Já o tópico _WARNING_, servirá para indicar que algo aconteceu parcialmente correto. Ex.: `Find and not read essentials.json`, `Visual Studio Code updated`.

E o _ERROR_ servirá para algo que deu completamente errado. Ex.: `Not found essentials.json`, `Visual Studio Code not installed and not updated`.

#### _Add Program_ na tela 2

Quando o usuário clicar em _Add Program_ na tela secundária, o sistema irá abrir a tela 3.1 descrita na parte de frontend. O sistema da barra de pesquisa pesquisará no sistema de gerenciador de pacotes, _ex.: WinGet no Windows_, e o botão que alterna entre _Add_ e _Remove_ que adicionará o nome e id do programa referente à um object que, quando clicado no botão _Submit_, esse object será salvo no arquivo user.json, no fim do array _data_, com na seguinte estrutura:

```json
{
  "name": "<nome_do_programa>",
  "type": "install",
  "id": "<id_do_programa>"
}
```

#### _Remove Program_ na tela 2

Quando o usuário clicar em _Remove Program_ também da tela secundária, abrirá a tela 3.2 que terá um funcionamento muito parecido da tela 2.1. A diferença é que enquanto a tela estiver carregando, o sistema listará e mostra todos os programas instalados e salvará o array no final do array _data_ no arquivo user, com a seguinte estrutura:

```json
{
  "name": "<nome_do_programa>",
  "type": "uninstall",
  "id": "<id_do_programa>"
}
```

para ser utilizado pelo gerenciador de pacotes, ex.: `winget uninstall -id <id-do-programa>`.

#### Configurações padrão do Terminal Windows, Linux e MacOS

Para Windows, todos os comandos _WinGet_ terão que possuir o comando `--accept-source-agreements --accept-package-agreements >nul 2>&1` no final da linha para filtrar barras de progresso e aceitar termos de serviço automaticamente.

Para Linux/MacOS, todos os comandos Bash/Zsh terão que possuir ao final da linha o comando `> /dev/null 2>&1`

E se tiver alguma execução em PowerShell, a execução terá que inserir no final da linha o comando `*> $null`

#### Execução em segundo plano

Quando o usuário clicar em _RUN_ na tela 2, todas as telas serão fechadas e o programa continuará somente em segundo plano. Simultaneamente ao fechamento, ele salvará no arquivo log.log a seguinte mensagem: `[dd/mm/aaaa hh:mm:ss] [INFO] Start system`. Também abrirá o compartilhamento do arquivo log.log em localhost HTTP na porta 9999 e abrirá o site [Programs Manager Website](https://programs-manager-website.vercel.app).

Logo após as primeiras execuções, o programa iniciará as tarefas principais na seguinte ordem:

- Atualizar o gerenciador de pacotes, exemplo Windows: _Microsoft.AppInstaller_;
- Chamar o sistema do [JSON Interno](#json-interno) e salvar esses dados no array _json_data_;
- Obter os dados pelo [JSON Externo](#json-externo) e irá salvá-los também no array _json_data_;
- Enquanto o sistema estiver lendo os arquivos JSONs, ele escreverá a seguinte mensagem no log.log para cada JSON:
  - Se for lido com sucesso:

    ````log
    [dd/mm/aaaa hh:mm:ss] [INFO] Read <nome_do_arquivo> successfully```
    ````

  - Se der erro:

    ````log
    [dd/mm/aaaa hh:mm:ss] [ERROR] Read <nome_do_arquivo> with error <erro>```
    ````

- Fazer um loop para cada object no _json_data_ e separar os seguintes dados:
  - O sistema faz outro loop para os dados do array _data_ e faz o seguinte com os objects:
    - Se o _type_ do object for `install`, salvará o object no array _install_;
    - Se o _type_ do object for `uninstall`, salvará o object no array _uninstall_;
    - Se o _type_ do object for `function`, salvará o object no array _function_;
- Depois executa cada função de acordo:
  - Primeiro desinstala os programas listados no array _uninstall_, utilizando o gerenciador de pacotes. Ex.: `winget uninstall -id <id_do_programa>`;
  - Depois executa os da _function_, que verificará as funções no sistema e executará a função referente ao dado;
  - Por fim, instalará os programas listados no _install_, também utilizando

## Site

Site que receberá os dados do arquivo log.log gerado pela execução do programa. Quando o programa é executado, ele abre uma aba no navegador com este site. Este projeto irá monitorar e retornar ao usuário os dados do arquivo em tempo real para que o usuário possa saber o progresso do programa.

Esse site será salvo no Github e terá hospedagem vinculada na Vercel.

### FRONT-END Site

#### Site Language

EN-US

#### Tela principal

Será mostrado três contêineres com os dados obtidos do Back-end com as seguintes informações:

- Cada contêiner conterá uma altura fixa, com uma barra de rolagem horizontal. Os dados serão mostrados de forma que os mais antigos aparecerão acima e os mais recentes aparecerão abaixo. O contêiner terá rolagem automática para enfatizar os últimos dados, mas se o usuário rolar para cima manualmente, a rolagem automática é pausada até o usuário rolar novamente ao fim dos dados;
- Os dados serão recebidos da seguinte forma:
  - Para informações:

    ```log
    [dd/mm/aaaa hh:mm:ss] [INFO] <mensagem>
    ```

  - Para semi-erros:

    ```log
    [dd/mm/aaaa hh:mm:ss] [WARNING] <mensagem>
    ```

  - Para erros completos

    ```log
    [dd/mm/aaaa hh:mm:ss] [ERROR] <mensagem>
    ```

- Os contêineres serão organizados de acordo com os resultados `INFO`, `WARNING` e `ERROR` e mostrarão somente os dados referentes;
- O dado que será recebido será do tipo: `[01/06/2026 12:30:45] [SUCCESS] Visual Studio Code installed`, e o que será mostrado para o usuário será da seguinte forma: `01/06/2026 12:30:45 | Visual Studio installed`, com a data e hora na cor `#808080` e a informação na cor padrão de texto do site;
- Abaixo, a segunda parte só aparecerá se o arquivo possuir um histórico além de somente o histórico da atual execução;
- Esse histórico será definido pelo cálculo de tolerância de 1 minuto de atraso a partir da abertura do site. Ex.: se no arquivo possuir a datação `[01/06/2026 00:00:00]` e o site possuir a datação `[01/06/2026 00:01:00]`, a informação da linha será mostrada na tela principal. Agora, se a datação do arquivo for a mesma, mas do site for `[01/06/2026 00:01:01]`, essa informação será mostrada na segunda parte onde será a partição de histórico de execuções anteriores. Esse sistema de filtro servirá para que o site de ênfase aos dados atuais, mas se o usuário quiser ver os dados de outras execuções ele consegue. O tempo de 1 minuto de tolerância a partir da execução do programa em relação a datação do site é para que se o site demorar para carregar, os dados da execução atual não irão para o histórico geral;

#### Rodapé

##### Container de contato

Nesse container será mostrado os contatos obtidos pelo [Contato](#contato) em forma de itens redondos, mostrando à primeira vista somente os ícones. O card terá um sistema em que ao passar o mouse por cima será mostrado o conteúdo da variável _name_, tipo o que a tag `title=""` faz. Carregará as informações do JSON obtido do repositório de portfólio pelo Back-end, e utilizando o dado _url_ para ser o href do link, e o _iconName_ será utilizado para dizer qual ícone será inserido dentro do link. A organização do container será assim:

```css
display: flex;
flex-flow: row wrap;
justify-content: space-between;
align-items: center;
```

#### Tela de Erro

Se o time hate for expedido, ao invés de aparecer a tela principal e secundária descritas acima, será mostrada uma mensagem dizendo que a porta 9999 não foi aberta ou o arquivo não foi compartilhado, e pede ao usuário que faça refresh na página ou reexecute o programa. Logo abaixo será mostrado um botão que levará ao repositório [Programs Manager](https://github.com/JLBBARCO/programs-manager).

### BACK-END Site

A cada vez que o site for aberto, ele armazenará temporariamente a data e hora de loading para ser utilizado pelos sistemas de filtros.

O sistema de filtro por datação será com base na seguinte informação com data e hora de exemplo:

```json
  [dd/mm/aaaa hh:mm:ss] [INFO] Start system
```

O sistema só irá parar de monitorar o arquivo quando a informação mais recente for:

```json
  [dd/mm/aaaa hh:mm:ss] [INFO] End system
```

#### Análise da porta

Quando o site for carregado, ele irá monitorar a porta 9999 por 30 segundos. Se ela não for aberta ou não for compartilhado o arquivo log.log por ela, o site irá parar de monitorar ela até que o usuário faça um refresh.

#### Contato

O site irá obter os contatos do [JSON](https://raw.githubusercontent.com/JLBBARCO/portfolio/main/src/json/areas/contact.json) e o sistema fará um loop com o array _cards_ e para cada object será criado um card com os dados relacionados, assim como previsto no [Rodapé](#rodapé).

A requisição desse json será feita pela Vercel a cada hora para que não tenha muitas requisições no github e que o site fique leve para o usuário.

## Github Actions

O Github Actions deverá compilar o programa em cada sistema operacional somente quando for branch main/master ou develop.

O Actions deverá utilizar os arquivos "build.bat", build.sh" e "build-mac.sh" para compilar para cada sistema operacional. Essa automação deverá armazenar a compilação em um arquivo de compactação, ex.: zip, e armazenará em um Github Release novo, mas seguindo algumas regras:

Se a branch do commit for a main, o Actions deverá salvar os compilados como Last Release;

Já se a branch for a beta, o Actions deverá salvar como Pre-release;

A pasta system não precisa ser incluída na compilação pois todos os arquivos contidos nela serão obtidos via Github RAW.

A automação também deverá gerar um print de cada sistema operacional utilizando o bot do Github. Esses prints serão em formato WEBP, e eles substituirão os arquivos:
![Print MacOS](src/assets/img/macos.webp)
![Print Linux](src/assets/img/linux.webp)
![Print Windows](src/assets/img/windows.webp)

Depois dos prints separados, será montada uma imagem com os três prints lado a lado, e substituirão o arquivo do caminho:
![Print from all system prints compiled](src/assets/img/thumbnail.webp)

## Github RAW

Os arquivos "./run.ps1" e "./run.sh" serão utilizados para baixar e rodar o sistema diretamente do terminal, tanto Windows quanto Linux quanto MacOS, baixando o compilado referente ao sistema operacional diretamente da Last Release. Os comandos utilizados serão:

- Windows:

  ```powershell
  irm https://raw.githubusercontent.com/JLBBARCO/programs-manager/main/run.ps1 | iex
  ```

- Linux:

  ```bash
  curl -fsSL https://raw.githubusercontent.com/JLBBARCO/programs-manager/main/run.sh | bash
  ```

- MacOS:

  ```bash
  curl -fsSL https://raw.githubusercontent.com/JLBBARCO/programs-manager/main/run.sh | bash
  ```

Branch opcional sobrescrita (utilizado para testes `develop`):

```powershell
$env:AIP_BRANCH='develop'; irm https://raw.githubusercontent.com/JLBBARCO/programs-manager/main/run.ps1 | iex
```

```bash
AIP_BRANCH=develop curl -fsSL https://raw.githubusercontent.com/JLBBARCO/programs-manager/main/run.sh | bash
```
