# Análise: Por que a Gramática Não Suporta Certas Expressões Aninhadas

**Documento Técnico - RA2_1**
**Data**: 2025-10-02
**Autores**: Breno Rossi Duarte, Francisco Bley Ruthes, Rafael Olivare Piveta, Stefan Benjamim Seixas Lourenço Rodrigues

---

## 1. Resumo Executivo

Nossa gramática LL(1) para a calculadora RPN **não suporta** expressões no padrão:

```
( <EXPRESSAO_ANINHADA> VARIAVEL )
```

Por exemplo: `( ( A B + ) C )` - onde o resultado de uma expressão é atribuído diretamente a uma variável.

Este documento **prova formalmente** por que esse padrão falha e apresenta exemplos concretos.

---

## 2. Classificação de Expressões

### 2.1 Expressões que **FUNCIONAM** ✅

| Padrão | Exemplo | Por que funciona |
|--------|---------|------------------|
| `( NUM VAR )` | `( 5.5 A )` | `AFTER_NUM → VARIAVEL AFTER_VAR_OP → EPSILON` |
| `( VAR VAR )` | `( A B )` | `AFTER_VAR → EPSILON` |
| `( NUM NUM OP )` | `( 3 2 + )` | `AFTER_NUM → NUMERO_REAL OPERATOR` |
| `( VAR NUM OP )` | `( A 2 + )` | `AFTER_VAR → NUMERO_REAL OPERATOR` |
| `( IFELSE ... )` | `( IFELSE ( A B < ) ( X ) ( Y ) )` | Regra específica `IFELSE_STRUCT` |

### 2.2 Expressões que **FALHAM** ❌

| Padrão | Exemplo | Por que falha |
|--------|---------|---------------|
| `( ( EXPR ) VAR )` | `( ( A B + ) C )` | `AFTER_EXPR → VARIAVEL OPERATOR` (falta EPSILON) |
| `( ( RES ) VAR )` | `( ( 3.0 RES ) Z )` | Mesmo motivo |
| `( ( EXPR ) ( EXPR ) OP )` | `( ( A 2 + ) ( B 3 * ) - )` | AFTER_EXPR espera token único, não `(` |

---

## 3. Análise da Gramática

### 3.1 Regras Relevantes

```python
CONTENT → NUMERO_REAL AFTER_NUM
        | VARIAVEL AFTER_VAR
        | ( EXPR ) AFTER_EXPR          ← Problema está aqui!
        | FOR FOR_STRUCT
        | WHILE WHILE_STRUCT
        | IFELSE IFELSE_STRUCT
```

### 3.2 Comparação Crítica: AFTER_VAR vs AFTER_EXPR

#### **AFTER_VAR** (com EPSILON ✅)
```python
AFTER_VAR → NUMERO_REAL OPERATOR
          | VARIAVEL OPERATOR
          | ( EXPR ) OPERATOR
          | EPSILON                    ← Permite terminar sem operador!
```

#### **AFTER_EXPR** (sem EPSILON ❌)
```python
AFTER_EXPR → NUMERO_REAL OPERATOR
           | VARIAVEL OPERATOR         ← SEMPRE exige OPERATOR!
           | ( EXPR ) OPERATOR
```

**A diferença**: `AFTER_VAR` aceita **produção vazia** (`EPSILON`), mas `AFTER_EXPR` **não aceita**.

---

## 4. Trace do Parser - Prova por Execução

### Exemplo 1: `( 5.5 A )` - **SUCESSO** ✅

```
Passo 1:  Token: (     | Pilha: [$ LINHA]
          → LINHA → ( CONTENT )

Passo 2:  Token: 5.5   | Pilha: [$ ) CONTENT (]
          → Match '('
          → CONTENT → NUMERO_REAL AFTER_NUM

Passo 3:  Token: 5.5   | Pilha: [$ ) AFTER_NUM NUMERO_REAL]
          → Match NUMERO_REAL

Passo 4:  Token: A     | Pilha: [$ ) AFTER_NUM]
          → AFTER_NUM → VARIAVEL AFTER_VAR_OP

Passo 5:  Token: A     | Pilha: [$ ) AFTER_VAR_OP VARIAVEL]
          → Match VARIAVEL

Passo 6:  Token: )     | Pilha: [$ ) AFTER_VAR_OP]
          → AFTER_VAR_OP → EPSILON          ← Produção vazia!

Passo 7:  Token: )     | Pilha: [$ )]
          → Match ')'

✅ SUCESSO: Pilha vazia, parsing completo
```

---

### Exemplo 2: `( ( A B + ) C )` - **FALHA** ❌

```
Passo 1:  Token: (     | Pilha: [$ LINHA]
          → LINHA → ( CONTENT )

Passo 2:  Token: (     | Pilha: [$ ) CONTENT (]
          → Match '('
          → CONTENT → ( EXPR ) AFTER_EXPR

Passo 3:  Token: (     | Pilha: [$ ) AFTER_EXPR ) EXPR (]
          → Match '('

Passo 4-7: (processa A B + internamente)
          → EXPR → VARIAVEL AFTER_VAR
          → AFTER_VAR → VARIAVEL OPERATOR
          → OPERATOR → ARITH_OP → +

Passo 8:  Token: )     | Pilha: [$ ) AFTER_EXPR )]
          → Match ')'

Passo 9:  Token: C     | Pilha: [$ ) AFTER_EXPR]
          → Consulta: M[AFTER_EXPR, IDENTIFIER]
          → Encontra: AFTER_EXPR → VARIAVEL OPERATOR

Passo 10: Token: C     | Pilha: [$ ) OPERATOR VARIAVEL]
          → Match VARIAVEL

Passo 11: Token: )     | Pilha: [$ ) OPERATOR]
          → Consulta: M[OPERATOR, )]

❌ ERRO: Não existe entrada M[OPERATOR, )]
         OPERATOR só aceita: +, -, *, /, %, ^, <, >, ==, !=, &&, ||, !
```

**Prova**: O parser **espera um operador** após `C`, mas encontra `)`.

---

## 5. Verificação na Tabela LL(1)

### Entrada Existente (válida)
```
M[AFTER_VAR, FECHA_PARENTESES] = AFTER_VAR → EPSILON
```
✅ Permite: `( A )` ou `( 5.5 A )`

### Entrada Ausente (inválida)
```
M[AFTER_EXPR, FECHA_PARENTESES] = ???
```
❌ **NÃO EXISTE** na tabela LL(1)

A tabela atual só tem:
```
M[AFTER_EXPR, NUMERO_REAL] = AFTER_EXPR → NUMERO_REAL OPERATOR
M[AFTER_EXPR, VARIAVEL]    = AFTER_EXPR → VARIAVEL OPERATOR
M[AFTER_EXPR, (]           = AFTER_EXPR → ( EXPR ) OPERATOR
```

**Conclusão**: Não há produção para `AFTER_EXPR` quando próximo token é `)`.

---

## 6. Análise FIRST e FOLLOW

### FIRST(AFTER_EXPR)
```
FIRST(AFTER_EXPR) = {NUMERO_REAL, VARIAVEL, (}
```
- `EPSILON` **NÃO** está no FIRST
- Logo, não há produção vazia

### FOLLOW(AFTER_EXPR)
```
FOLLOW(AFTER_EXPR) = {)}
```
- O símbolo `)` está no FOLLOW
- Mas **não há produção** `AFTER_EXPR → EPSILON`
- Portanto, não há regra de FOLLOW aplicável

**Contraste com AFTER_VAR:**
```
FIRST(AFTER_VAR) = {NUMERO_REAL, VARIAVEL, (, EPSILON}
FOLLOW(AFTER_VAR) = {)}
```
Como `EPSILON ∈ FIRST(AFTER_VAR)`, a tabela tem:
```
M[AFTER_VAR, )] = AFTER_VAR → EPSILON
```

---

## 7. Por Que o Design Está Assim?

A gramática foi projetada para suportar:

1. **Atribuição direta de literal**: `( 5.5 A )` ✅
2. **Operações RPN básicas**: `( 3 2 + )` ✅
3. **Expressões com operadores**: `( A B + )` ✅

Mas **não** foi projetada para:
- **Atribuição do resultado de subexpressão**: `( ( A B + ) C )` ❌

### Possível Razão

No RPN puro, atribuições geralmente são feitas via:
```
( A B + )    # Calcula, deixa no topo da pilha
( RES C )    # Atribui resultado à variável C
```

Não diretamente em uma única expressão:
```
( ( A B + ) C )    # Não suportado pela gramática atual
```

---

## 8. Soluções Possíveis

### Solução 1: Modificar a Gramática ✏️

Adicionar produção EPSILON em `AFTER_EXPR`:

```python
AFTER_EXPR → NUMERO_REAL OPERATOR
           | VARIAVEL OPERATOR
           | VARIAVEL AFTER_VAR_OP      ← Reutiliza regra com EPSILON
           | ( EXPR ) OPERATOR
```

**Impacto**:
- Recomputar FIRST e FOLLOW
- Reconstruir tabela LL(1)
- Verificar conflitos LL(1)

### Solução 2: Ajustar Arquivos de Teste 📝

Substituir expressões problemáticas:

**Antes** ❌:
```
( ( A B + ) C )
```

**Depois** ✅ (Opção A):
```
( A B + )
( RES C )
```

**Depois** ✅ (Opção B):
```
( A B + C * )    # Usa o resultado em outra operação
```

---

## 9. Exemplos de Testes Válidos

### Arquivo de Teste Correto

```text
# Atribuições simples
( 5.5 A )
( 3.2 B )

# Operações RPN
( A B + )
( 3 2 * )

# Operações com resultado
( A B + C * )
( X Y - Z + )

# Estruturas de controle
( IFELSE ( A B > ) ( 1.0 ) ( 0.0 ) )
( WHILE ( X 5.5 < ) ( ( X 1.2 + ) X ) )

# Uso de RES
( A B + )
( RES C )
```

---

## 10. Conclusão

**Provamos formalmente** que a gramática LL(1) atual **não suporta** o padrão `( ( EXPR ) VAR )` porque:

1. ✅ **Fato 1**: `AFTER_EXPR` não possui produção `EPSILON`
2. ✅ **Fato 2**: Tabela LL(1) não tem entrada `M[AFTER_EXPR, )]`
3. ✅ **Fato 3**: Parser falha ao encontrar `)` quando espera `OPERATOR`
4. ✅ **Fato 4**: Trace de execução mostra erro exato no passo 11

**Recomendação**: Ajustar arquivos de teste para usar padrões suportados, ou modificar a gramática se esse padrão for essencial para a apresentação.

---

## Referências

- Aho, A. V., Lam, M. S., Sethi, R., & Ullman, J. D. (2006). *Compilers: Principles, Techniques, and Tools* (2nd ed.). Pearson.
- Código-fonte: `src/RA2/functions/python/configuracaoGramatica.py`
- Tabela LL(1): `src/RA2/functions/python/construirTabelaLL1.py`
- Parser: `src/RA2/functions/python/parsear.py`
