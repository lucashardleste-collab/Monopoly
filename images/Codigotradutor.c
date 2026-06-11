#include <stdio.h>
#include <string.h>
#include <stdlib.h>

typedef struct{
    char comando[10];
    unsigned char opcode;
    int bytes;
}lista;

int linhas_validas = 0;
int flag = 0;

char texto_linha[30];

int hexa_check(char *str){
    int i = 0;
    if(strlen(str) != 2){
        return 0;
    }
    while(str[i] != '\0'){
        if(!((str[i] >= 'A' && str[i] <= 'F') || (str[i] >= '0' && str[i] <= '9') || (str[i] >= 'a' && str[i] <= 'f'))){
            return 0;
        }
        i++;
    }
    return 1;
}
int main(void){

    char *instrucao;
    char *operando;


    FILE *arquivo;
    FILE *saida;

    lista texto [11] = {{"NOP", 0x00 , 0},
                        {"STA", 0x10, 1},
                        {"LDA", 0x20, 1},
                        {"ADD", 0x30, 1},
                        {"OR", 0x40, 1},
                        {"AND", 0x50, 1},
                        {"NOT", 0x60, 0},
                        {"JMP", 0x80, 1},
                        {"JN", 0x90, 1},
                        {"JZ", 0xA0, 1},
                        {"HLT", 0xF0, 0},};

    arquivo = fopen("entrada.asm", "r");

    saida = fopen("saida.mem", "wb");

    unsigned char cabecalho[] = {0x03, 0x4E, 0x44, 0x52};

    fwrite(cabecalho, sizeof(unsigned char), 4, saida);

    if(arquivo == NULL){
        printf("Erro ao abrir arquivo\n");
        return 1;
    }

    while (fgets(texto_linha, 30, arquivo) != NULL){
        
        int flag = 0;
        int flag_op = 0;

        instrucao = strtok(texto_linha, " \n");
        operando = strtok(NULL, " \n");

        if(instrucao == NULL){
            continue;
        }
        for (int i = 0; i < 11; i++){
            if(strcmp(instrucao, texto[i].comando) == 0){
                linhas_validas++;
                flag++;

                if(operando == NULL){
                    flag_op++;
                }

                if(texto[i].bytes == 1 && operando == NULL){
                    printf("O comando: '%s' exige operando\n", instrucao);
                    flag_op++;
                    break;
                }

                if(texto[i].bytes == 0 && operando != NULL){
                    printf("O comando: '%s' nao pode conter operando\n", instrucao);
                    flag_op++;
                    break;
                }

                fputc(texto[i].opcode, saida);
                fputc(0x00, saida);

                if(texto[i].bytes == 1 && operando != NULL){
                    if(!hexa_check(operando)){
                        break;
                    }
                    int valor = (int)strtol(operando, NULL, 16);
                    fputc(valor, saida);
                    fputc(0x00, saida);
                    flag_op++;
                }
                break;
            }
        }
        if(flag == 0){
            printf("O comando: '%s' NAO e valido. Digite um comando valido\n", instrucao);
            break;
        }
        if(flag_op == 0){
            printf("O operando %s e invalido", operando);
            break;
        }
    }

    if(linhas_validas == 0){
        printf("Arquivo ASM vazio\n");
        return 1;
    }

    if(saida == NULL){
        printf("Erro ao criar arquivo\n");
        return 1;
    }

    fclose(arquivo);
    fclose(saida);
    
    return 0;
}


