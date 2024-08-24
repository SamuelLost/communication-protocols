#include <Arduino.h>

#include "MFRC522.h" //biblioteca responsável pela comunicação com o módulo RFID-RC522
#include <SPI.h> //biblioteca para comunicação do barramento SPI

#define SS_PIN    21
#define RST_PIN   22

#define SIZE_BUFFER     18
#define MAX_SIZE_BLOCK  16

void ler_tudo();
int menu();
void leitura_dados();
void escreve_dados();

//Objeto 'chave' é utilizado para autenticação
MFRC522::MIFARE_Key key;

//código de status de retorno da autenticação
MFRC522::StatusCode status;

// Definicoes pino modulo RC522
MFRC522 mfrc522(SS_PIN, RST_PIN);

void setup() {
  // Inicia a serial
  Serial.begin(115200);
  SPI.begin(); // Init SPI bus

  // Inicia MFRC522
  mfrc522.PCD_Init();

  // Prepara a chave - todas as chaves estão configuradas para FFFFFFFFFFFFh (Padrão de fábrica).
  for (uint8_t i = 0; i < 6; i++) key.keyByte[i] = 0xFF;

  // Mensagens iniciais no serial monitor
  Serial.println("\nAproxime o seu cartao do leitor...");

}

void loop() {
  // Aguarda a aproximacao do cartao e Seleciona um dos cartoes
  if (!mfrc522.PICC_IsNewCardPresent() || !mfrc522.PICC_ReadCardSerial()) {
    return;
  }

  switch (menu()) {
  case 1:
    ler_tudo();
    break;
  case 2:
    leitura_dados();
    break;
  case 3:
    escreve_dados();
    break;
  default:
    Serial.println(F("Opção inválida!"));
    break;
  }
  // instrui o PICC quando no estado ACTIVE a ir para um estado de "parada"
  mfrc522.PICC_HaltA();
  // "stop" a encriptação do PCD, deve ser chamado após a comunicação com autenticação, caso contrário novas comunicações não poderão ser iniciadas
  mfrc522.PCD_StopCrypto1();
}

//faz a leitura dos dados do cartão/tag
void ler_tudo() {
  MFRC522::PICC_Type piccType = mfrc522.PICC_GetType(mfrc522.uid.sak);
  // //imprime os detalhes tecnicos do cartão/tag
  mfrc522.PICC_DumpDetailsToSerial(&(mfrc522.uid));

  mfrc522.PICC_DumpMifareClassicToSerial(&(mfrc522.uid), piccType, &key);
}

int menu() {
  Serial.println(F("\nEscolha uma opção:"));
  Serial.println(F("1 - Ler todo o cartão"));
  Serial.println(F("2 - Leitura de Dados"));
  Serial.println(F("3 - Escrever Dados"));

  //fica aguardando enquanto o usuário nao enviar algum dado
  while (!Serial.available()) {};

  //recupera a opção escolhida
  int op = (int)Serial.read();
  //remove os proximos dados (como o 'enter ou \n' por exemplo) que vão por acidente
  while (Serial.available()) {
    if (Serial.read() == '\n') break;
    Serial.read();
  }
  return (op - 48);//do valor lido, subtraimos o 48 que é o ZERO da tabela ascii
}

void leitura_dados() {
  //imprime os detalhes tecnicos do cartão/tag
  mfrc522.PICC_DumpDetailsToSerial(&(mfrc522.uid));

  uint8_t num_cartao[4];
  num_cartao[0] = mfrc522.uid.uidByte[3];
  num_cartao[1] = mfrc522.uid.uidByte[2];
  num_cartao[2] = mfrc522.uid.uidByte[1];
  num_cartao[3] = mfrc522.uid.uidByte[0];

  // unsigned int num = num_cartao[0] << 24 | num_cartao[1] << 16 | num_cartao[2] << 8 | num_cartao[3];
  unsigned int num = mfrc522.uid.uidByte[3] << 24 | mfrc522.uid.uidByte[2] << 16 | mfrc522.uid.uidByte[1] << 8 | mfrc522.uid.uidByte[0];

  Serial.printf("Número do cartão: %010u [", num);
  for (uint8_t i = 0; i < 4; i++) {
    Serial.printf("%02X", num_cartao[i]);
  }
  Serial.println("]");

  //buffer para colocar os dados ligos
  uint8_t buffer[SIZE_BUFFER] = { 0 };

  //bloco que faremos a operação
  uint8_t bloco = 0;
  uint8_t tamanho = SIZE_BUFFER;


  //faz a autenticação do bloco que vamos operar
  status = mfrc522.PCD_Authenticate(MFRC522::PICC_CMD_MF_AUTH_KEY_A, bloco, &key, &(mfrc522.uid)); //line 834 of MFRC522.cpp file
  if (status != MFRC522::STATUS_OK) {
    Serial.print(F("Authentication failed: "));
    Serial.println(mfrc522.GetStatusCodeName(status));
    return;
  }

  //faz a leitura dos dados do bloco
  for (int i = 0; i < 4; i++) {
    status = mfrc522.MIFARE_Read(i, buffer, &tamanho);
    if (status != MFRC522::STATUS_OK) {
      Serial.print(F("Falha ao ler: "));
      Serial.println(mfrc522.GetStatusCodeName(status));
      return;
    }

    Serial.printf("Dados do bloco [%d]: ", i);

    //imprime os dados lidos
    for (uint8_t j = 0; j < MAX_SIZE_BLOCK; j++) {
      Serial.write(buffer[j]);
    }
    Serial.println(" ");
  }
}

void escreve_dados() {
  //imprime os detalhes tecnicos do cartão/tag
  mfrc522.PICC_DumpDetailsToSerial(&(mfrc522.uid));
  // aguarda 30 segundos para entrada de dados via Serial
  Serial.setTimeout(30000L);
  Serial.println(F("Insira os dados a serem gravados com o caractere '#' ao final\n[máximo de 16 caracteres]:"));

  //Prepara a chave - todas as chaves estão configuradas para FFFFFFFFFFFFh (Padrão de fábrica).
  // for (uint8_t i = 0; i < 6; i++) key.keyByte[i] = 0xFF;

  //buffer para armazenamento dos dados que iremos gravar
  uint8_t buffer[MAX_SIZE_BLOCK] = "";
  uint8_t bloco; //bloco que desejamos realizar a operação
  uint8_t tamanhoDados; //tamanho dos dados que vamos operar (em bytes)

  //recupera no buffer os dados que o usuário inserir pela serial
  //serão todos os dados anteriores ao caractere '#'
  tamanhoDados = Serial.readBytesUntil('#', (char*)buffer, MAX_SIZE_BLOCK);
  //espaços que sobrarem do buffer são preenchidos com espaço em branco
  for (uint8_t i = tamanhoDados; i < MAX_SIZE_BLOCK; i++) {
    buffer[i] = ' ';
  }

  bloco = 1;
  Serial.printf("Dados a serem gravados: %.*s\n", tamanhoDados, buffer);

  //Authenticate é um comando para autenticação para habilitar uma comuinicação segura
  status = mfrc522.PCD_Authenticate(MFRC522::PICC_CMD_MF_AUTH_KEY_A,
    bloco, &key, &(mfrc522.uid));

  if (status != MFRC522::STATUS_OK) {
    Serial.print(F("Falha ao autenticar cartão: "));
    Serial.println(mfrc522.GetStatusCodeName(status));
    return;
  }

  //Grava no bloco
  status = mfrc522.MIFARE_Write(bloco, buffer, MAX_SIZE_BLOCK);
  if (status != MFRC522::STATUS_OK) {
    Serial.print(F("Falha ao gravar o cartão: "));
    Serial.println(mfrc522.GetStatusCodeName(status));
    return;
  }
  else {
    Serial.println(F("Cartão gravado com sucesso!"));
  }
}
