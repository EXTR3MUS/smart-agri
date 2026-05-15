# [T1GA] Controlador de Microclima Automatizado para Agricultura de Precisão em estufas 

## a) Contexto e funcionamento

### Contexto:
Controlador de Microclima Automatizado para Agricultura de Precisão (Smart Agriculture) em estufas. Atua como interface física (Edge) para a coleta e envio de dados em tempo real para um sistema de Gêmeos Digitais (Digital Twins). Trabalho desenvolvido de acordo com a temática do projeto que estou trabalhando como pesquisador.

### Funcionamento e Papel no Sistema
1. Sensoriamento: Coleta de variáveis ambientais: temperatura e umidade do ar, umidade do solo e luminosidade.
2. Atuação: Gerencia o acionamento de periféricos de potência via relés: bomba d'água para irrigação e exaustor para ventilação.
3. Automação e Controle: Executa controle local autônomo baseado em setpoints internos e aceita comandos de escrita remota vindos de um Client para override ou modificação do setpoint.

## b) Lista de Variáveis Relevantes

1. Temperatura do Ar
2. Umidade do Solo
3. Modo de Operação (Automático / Manual)
4. Setpoint de Umidade do Solo
5. Estado/Comando da Bomba d'Água
6. Estado/Comando do Exaustor

## c) Mapeamento de Dados Modbus

| Variável | Tipo Modbus | Endereço | Descrição | Unidade | Faixa de Valores |
| :--- | :--- | :--- | :--- | :--- | :--- |
| Temperatura do Ar | Input Register | 30001 | Temperatura ambiente da estufa | °C (x10) | -100 a 850 (-10.0°C a 85.0°C) |
| Umidade do Solo | Input Register | 30002 | Percentual de água no solo | % | 0 a 100 |
| Estado da Bomba | Coil | 00001 | Status de acionamento do relé da bomba | On/Off | 0 (Desligado) ou 1 (Ligado) |
| Estado do Exaustor | Coil | 00002 | Status de acionamento do relé do exaustor | On/Off | 0 (Desligado) ou 1 (Ligado) |
| Modo de Operação | Holding Register | 40001 | Define lógica local ou remota | Adimensional | 0 (Manual) ou 1 (Automático) |
| Setpoint Umidade | Holding Register | 40002 | Limiar para ativação automática da bomba | % | 0 a 100 |

*Nota de projeto*: Variáveis analógicas fracionárias (como Temperatura) são multiplicadas por 10 no Server antes do envio para trafegar como inteiro de 16 bits. O Client deve aplicar o fator de escala 0.1 na recepção.

## d) Plataforma de Hardware e Justificativa Técnica

**Plataforma Escolhida**: ESP32 DevKit V1.

**Justificativa**:
1. **Conectividade Nativa**: Possui módulos Wi-Fi (802.11 b/g/n) e Bluetooth integrados, eliminando a necessidade de shields externos de rede para a comunicação Modbus TCP.
2. **Capacidade de Processamento**: Processador poderoso de 32 bits e dois núcleos  rodando a 240 MHz. Permite dedicar um núcleo exclusivamente para as tarefas críticas de rede (pilha TCP/IP e Modbus Server) e o outro para a leitura de sensores e controle dos atuadores.
3. **Relação Custo-Benefício e Escalabilidade**: Hardware de baixo custo e ampla aceitação em prototipagem industrial/IoT, ideal para arquiteturas distribuídas com múltiplos nós sensores em campo.

## e) Avaliação de Bibliotecas Prontas

**Biblioteca Avaliada**: ModbusIP_ESP32.

**Vantagens**:
1. **Abstração de Protocolo**: Gerencia nativamente a montagem e desmontagem do cabeçalho MBAP (Modbus Application Protocol), permitindo manipular os dados diretamente pelas funções de leitura/escrita de registradores.
2. **Gerenciamento de Conexões**: Controla de forma transparente a abertura e fechamento de sockets TCP na porta padrão 502.
3. **Suporte a Callbacks**: Permite associar funções específicas do firmware a eventos de escrita do Client, otimizando o tempo de resposta do sistema de controle.

**Limitações**:
1. **Não possui Segurança Nativa**: A biblioteca não implementa criptografia (Modbus TCP Security com TLS). Os dados trafegam em texto claro, exigindo redes locais isoladas (VLANs) ou VPNs para proteção.
2. Bloqueio de Sockets: Se houver instabilidade severa no Wi-Fi, o tratamento de timeout interno da biblioteca pode causar travamentos momentâneos no laço principal se não houver um watchdog configurado.

## f) Variante do Modbus e Justificativa

**Variante Escolhida**: Modbus TCP.

**Justificativa**:
1. **Infraestrutura Existente**: Aproveita a rede sem fio (Wi-Fi) já disponível no ambiente da estufa, reduzindo custos com cabeamento estruturado.
2. **Desempenho**: Taxa de transmissão drasticamente superior em comparação com o Modbus RTU serial (RS-485), reduzindo a latência no envio de dados para o modelo de Gêmeo Digital.
3. **Endereçamento Simplificado**: Dispensa o uso de Slave IDs físicos limitados (1-247). A identificação do dispositivo ocorre diretamente através do endereço IP na rede, simplificando o roteamento e a expansão do sistema.

## g) Arquitetura da Rede de Comunicação

1. **Topologia**: Estrela. Todos os nós controladores (Modbus TCP Servers) conectam-se diretamente a um Ponto de Acesso Central (Access Point/Roteador Wi-Fi).
2. **Meio Físico**: Ondas de radiofrequência na banda de 2.4 GHz, operando sob o padrão IEEE 802.11b/g/n.
3. **Papeis na Rede**:
   - Modbus TCP Server: O controlador em campo (ESP32) opera como Server, escutando requisições na porta lógica 502. Ele não inicia conexões, apenas responde às solicitações de leitura ou comandos de escrita.
   - Modbus TCP Client: A central de processamento (Dashboard, SCADA ou script de controle central) opera como Client, iniciando conexões TCP orientadas para ler os sensores ou enviar comandos de atuação.
4. **Endereçamento**: Configuração de IP Estático para o controlador, garantindo que o Client remoto sempre localize o Server sem dependência de resoluções dinâmicas de DHCP.