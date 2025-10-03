#!/usr/bin/env python3
"""
Vigorous LL(1) Grammar Testing Suite
Test the Updated_LL1_Grammar_PDF_Compliant against enhanced_grammar_test_cases

This implementation creates a comprehensive LL(1) parser and runs all test cases
to validate the grammar's capability and PDF compliance.
"""

import re
from typing import List, Dict, Tuple, Optional, Set
from enum import Enum
from dataclasses import dataclass

class TokenType(Enum):
    # Basic symbols
    NUMERO_REAL = "NUMERO_REAL"
    VARIAVEL = "VARIAVEL"
    ABRE_PARENTESES = "ABRE_PARENTESES"
    FECHA_PARENTESES = "FECHA_PARENTESES"
    RES = "RES"
    FIM = "FIM"

    # Arithmetic operators (PDF compliant)
    SOMA = "SOMA"
    SUBTRACAO = "SUBTRACAO"
    MULTIPLICACAO = "MULTIPLICACAO"
    DIVISAO_REAL = "DIVISAO_REAL"        # | operator (PDF compliant)
    DIVISAO_INTEIRA = "DIVISAO_INTEIRA"  # / operator (PDF compliant)
    RESTO = "RESTO"
    POTENCIA = "POTENCIA"

    # Relational operators
    MENOR = "MENOR"
    MAIOR = "MAIOR"
    MENOR_IGUAL = "MENOR_IGUAL"
    MAIOR_IGUAL = "MAIOR_IGUAL"
    IGUAL = "IGUAL"
    DIFERENTE = "DIFERENTE"

    # Logical operators
    AND = "AND"
    OR = "OR"
    NOT = "NOT"

    # Control structure keywords
    FOR = "FOR"
    WHILE = "WHILE"
    IFELSE = "IFELSE"

@dataclass
class Token:
    type: TokenType
    value: str
    line: int = 1
    column: int = 1

class PDFCompliantLexer:
    """PDF compliant lexer with correct division operator tokenization"""

    def __init__(self):
        # PDF compliant token mapping
        self.token_mapping = {
            '(': TokenType.ABRE_PARENTESES,
            ')': TokenType.FECHA_PARENTESES,
            '+': TokenType.SOMA,
            '-': TokenType.SUBTRACAO,
            '*': TokenType.MULTIPLICACAO,
            '|': TokenType.DIVISAO_REAL,      # PDF: Real division (pipe symbol)
            '/': TokenType.DIVISAO_INTEIRA,   # PDF: Integer division (slash symbol)
            '%': TokenType.RESTO,
            '^': TokenType.POTENCIA,
            '>': TokenType.MAIOR,
            '<': TokenType.MENOR,
            '>=': TokenType.MAIOR_IGUAL,
            '<=': TokenType.MENOR_IGUAL,
            '==': TokenType.IGUAL,
            '!=': TokenType.DIFERENTE,
            '&&': TokenType.AND,
            '||': TokenType.OR,
            '!': TokenType.NOT,
            'AND': TokenType.AND,
            'OR': TokenType.OR,
            'NOT': TokenType.NOT,
            'FOR': TokenType.FOR,
            'WHILE': TokenType.WHILE,
            'IFELSE': TokenType.IFELSE,
            'RES': TokenType.RES,
        }

    def tokenize(self, text: str) -> List[Token]:
        """Tokenize input text according to PDF specification"""
        tokens = []
        i = 0
        line = 1
        column = 1

        while i < len(text):
            # Skip whitespace
            if text[i].isspace():
                if text[i] == '\n':
                    line += 1
                    column = 1
                else:
                    column += 1
                i += 1
                continue

            # Check for two-character operators first
            if i + 1 < len(text):
                two_char = text[i:i+2]
                if two_char in self.token_mapping:
                    tokens.append(Token(self.token_mapping[two_char], two_char, line, column))
                    i += 2
                    column += 2
                    continue

            # Single character operators and parentheses
            if text[i] in self.token_mapping:
                tokens.append(Token(self.token_mapping[text[i]], text[i], line, column))
                i += 1
                column += 1
                continue

            # Numbers (integers or floats)
            if text[i].isdigit():
                start = i
                while i < len(text) and (text[i].isdigit() or text[i] == '.'):
                    i += 1
                value = text[start:i]
                tokens.append(Token(TokenType.NUMERO_REAL, value, line, column))
                column += len(value)
                continue

            # Variables and keywords (uppercase sequences)
            if text[i].isupper():
                start = i
                while i < len(text) and text[i].isupper():
                    i += 1
                value = text[start:i]

                # Check if it's a keyword
                if value in self.token_mapping:
                    tokens.append(Token(self.token_mapping[value], value, line, column))
                else:
                    tokens.append(Token(TokenType.VARIAVEL, value, line, column))
                column += len(value)
                continue

            # Unrecognized character
            raise SyntaxError(f"Unrecognized character '{text[i]}' at line {line}, column {column}")

        # Add end-of-file marker
        tokens.append(Token(TokenType.FIM, "FIM", line, column))
        return tokens

class LL1Parser:
    """LL(1) parser implementing the PDF compliant grammar"""

    def __init__(self):
        # PDF compliant grammar from Updated_LL1_Grammar_PDF_Compliant.md
        self.grammar = {
            'PROGRAM': [['LINHA', 'PROGRAM_PRIME']],
            'PROGRAM_PRIME': [['LINHA', 'PROGRAM_PRIME'], ['EPSILON']],
            'LINHA': [['ABRE_PARENTESES', 'CONTENT', 'FECHA_PARENTESES']],
            'CONTENT': [
                ['NUMERO_REAL', 'AFTER_NUM'],
                ['VARIAVEL', 'AFTER_VAR'],
                ['ABRE_PARENTESES', 'EXPR', 'FECHA_PARENTESES', 'AFTER_EXPR'],
                ['FOR', 'FOR_STRUCT'],
                ['WHILE', 'WHILE_STRUCT'],
                ['IFELSE', 'IFELSE_STRUCT']
            ],
            'AFTER_NUM': [
                ['NUMERO_REAL', 'OPERATOR'],
                ['VARIAVEL', 'AFTER_VAR_OP'],
                ['ABRE_PARENTESES', 'EXPR', 'FECHA_PARENTESES', 'OPERATOR'],
                ['NUMERO_REAL', 'OPERATOR', 'VARIAVEL'],  # Store arithmetic result in memory
                ['VARIAVEL', 'OPERATOR', 'VARIAVEL'],     # Store arithmetic result in memory
                ['VARIAVEL'],                             # Store number in memory (no operator)
                ['RES']
            ],
            'AFTER_VAR_OP': [['OPERATOR'], ['EPSILON']],
            'AFTER_VAR': [
                ['NUMERO_REAL', 'OPERATOR'],
                ['VARIAVEL', 'OPERATOR'],
                ['ABRE_PARENTESES', 'EXPR', 'FECHA_PARENTESES', 'OPERATOR'],
                ['EPSILON']
            ],
            'AFTER_EXPR': [
                ['NUMERO_REAL', 'OPERATOR'],
                ['VARIAVEL', 'AFTER_VAR_OP'],
                ['ABRE_PARENTESES', 'EXPR', 'FECHA_PARENTESES', 'OPERATOR'],
                ['UNARY_OP']                              # Unary operator support
            ],
            'EXPR': [
                ['NUMERO_REAL', 'AFTER_NUM'],
                ['VARIAVEL', 'AFTER_VAR'],
                ['ABRE_PARENTESES', 'EXPR', 'FECHA_PARENTESES', 'AFTER_EXPR']
            ],
            'OPERATOR': [['ARITH_OP'], ['COMP_OP'], ['LOGIC_OP']],
            'ARITH_OP': [
                ['SOMA'], ['SUBTRACAO'], ['MULTIPLICACAO'],
                ['DIVISAO_REAL'], ['DIVISAO_INTEIRA'],  # PDF compliant division
                ['RESTO'], ['POTENCIA']
            ],
            'COMP_OP': [
                ['MENOR'], ['MAIOR'], ['IGUAL'],
                ['MENOR_IGUAL'], ['MAIOR_IGUAL'], ['DIFERENTE']
            ],
            'LOGIC_OP': [['AND'], ['OR'], ['NOT']],
            'UNARY_OP': [['NOT']],                       # Unary logical operators
            'FOR_STRUCT': [['NUMERO_REAL', 'NUMERO_REAL', 'VARIAVEL', 'LINHA']],
            'WHILE_STRUCT': [['ABRE_PARENTESES', 'EXPR', 'FECHA_PARENTESES', 'LINHA']],
            'IFELSE_STRUCT': [['ABRE_PARENTESES', 'EXPR', 'FECHA_PARENTESES', 'LINHA', 'LINHA']]
        }

        # Build parsing table
        self.parsing_table = self._build_parsing_table()

    def _calculate_first_sets(self) -> Dict[str, Set[str]]:
        """Calculate FIRST sets for all symbols"""
        first_sets = {}

        # Initialize FIRST sets
        for non_terminal in self.grammar:
            first_sets[non_terminal] = set()

        # Add terminals
        for token_type in TokenType:
            first_sets[token_type.value] = {token_type.value}
        first_sets['EPSILON'] = {'EPSILON'}

        # Calculate FIRST sets using fixed-point algorithm
        changed = True
        while changed:
            changed = False
            for non_terminal in self.grammar:
                old_size = len(first_sets[non_terminal])

                for production in self.grammar[non_terminal]:
                    if production == ['EPSILON']:
                        first_sets[non_terminal].add('EPSILON')
                        continue

                    for symbol in production:
                        first_sets[non_terminal].update(first_sets[symbol] - {'EPSILON'})
                        if 'EPSILON' not in first_sets[symbol]:
                            break
                    else:
                        # All symbols can derive epsilon
                        first_sets[non_terminal].add('EPSILON')

                if len(first_sets[non_terminal]) > old_size:
                    changed = True

        return first_sets

    def _calculate_follow_sets(self, first_sets: Dict[str, Set[str]]) -> Dict[str, Set[str]]:
        """Calculate FOLLOW sets for all non-terminals"""
        follow_sets = {}

        # Initialize FOLLOW sets
        for non_terminal in self.grammar:
            follow_sets[non_terminal] = set()

        # Start symbol gets end-of-input marker
        follow_sets['PROGRAM'] = {'FIM'}

        # Calculate FOLLOW sets using fixed-point algorithm
        changed = True
        while changed:
            changed = False

            for non_terminal in self.grammar:
                for production in self.grammar[non_terminal]:
                    for i, symbol in enumerate(production):
                        if symbol in self.grammar:  # Is non-terminal
                            old_size = len(follow_sets[symbol])

                            # Add FIRST of everything after this symbol
                            if i + 1 < len(production):
                                for j in range(i + 1, len(production)):
                                    follow_sets[symbol].update(first_sets[production[j]] - {'EPSILON'})
                                    if 'EPSILON' not in first_sets[production[j]]:
                                        break
                                else:
                                    # All following symbols can derive epsilon
                                    follow_sets[symbol].update(follow_sets[non_terminal])
                            else:
                                # Last symbol in production
                                follow_sets[symbol].update(follow_sets[non_terminal])

                            if len(follow_sets[symbol]) > old_size:
                                changed = True

        return follow_sets

    def _build_parsing_table(self) -> Dict[Tuple[str, str], List[str]]:
        """Build LL(1) parsing table"""
        first_sets = self._calculate_first_sets()
        follow_sets = self._calculate_follow_sets(first_sets)

        parsing_table = {}

        for non_terminal in self.grammar:
            for production in self.grammar[non_terminal]:
                # Add entries for all terminals in FIRST(production)
                if production == ['EPSILON']:
                    # Add entries for all terminals in FOLLOW(non_terminal)
                    for terminal in follow_sets[non_terminal]:
                        if terminal != 'EPSILON':
                            parsing_table[(non_terminal, terminal)] = production
                else:
                    for symbol in production:
                        for terminal in first_sets[symbol]:
                            if terminal != 'EPSILON':
                                parsing_table[(non_terminal, terminal)] = production
                        if 'EPSILON' not in first_sets[symbol]:
                            break
                    else:
                        # All symbols can derive epsilon
                        for terminal in follow_sets[non_terminal]:
                            if terminal != 'EPSILON':
                                parsing_table[(non_terminal, terminal)] = production

        return parsing_table

    def parse(self, tokens: List[Token]) -> Tuple[bool, List[str], str]:
        """
        Parse tokens using LL(1) parser
        Returns: (success, derivation_sequence, error_message)
        """
        try:
            stack = ['FIM', 'PROGRAM']  # Bottom-up: FIM, then start symbol
            input_tokens = [token.type.value for token in tokens]
            input_index = 0
            derivation = []

            while len(stack) > 1:  # While not just FIM on stack
                top = stack[-1]
                current_input = input_tokens[input_index] if input_index < len(input_tokens) else 'FIM'

                if top == current_input:
                    # Terminal match
                    stack.pop()
                    input_index += 1
                    derivation.append(f"Match terminal: {top}")
                elif top in self.grammar:
                    # Non-terminal - use parsing table
                    table_key = (top, current_input)
                    if table_key in self.parsing_table:
                        production = self.parsing_table[table_key]
                        stack.pop()

                        if production != ['EPSILON']:
                            # Add production symbols in reverse order
                            for symbol in reversed(production):
                                stack.append(symbol)

                        derivation.append(f"{top} → {' '.join(production)}")
                    else:
                        return False, derivation, f"No rule for ({top}, {current_input}) in parsing table"
                else:
                    return False, derivation, f"Unexpected symbol on stack: {top}"

            # Check if all input consumed
            if input_index < len(input_tokens) - 1:  # -1 for FIM token
                return False, derivation, f"Input not fully consumed. Remaining: {input_tokens[input_index:]}"

            return True, derivation, "Parse successful"

        except Exception as e:
            return False, [], f"Parse error: {str(e)}"

class GrammarTestRunner:
    """Comprehensive test runner for grammar validation"""

    def __init__(self):
        self.lexer = PDFCompliantLexer()
        self.parser = LL1Parser()
        self.test_results = []
        self.real_world_results = []

    def run_test(self, test_name: str, input_text: str, expected_success: bool, description: str = "") -> bool:
        """Run a single test case"""
        print(f"\n🔍 Testing: {test_name}")
        print(f"📝 Input: {input_text}")
        print(f"📋 Description: {description}")

        try:
            # Tokenize
            tokens = self.lexer.tokenize(input_text)
            print(f"🔤 Tokens: {[f'{t.type.value}({t.value})' for t in tokens if t.type != TokenType.FIM]}")

            # Parse
            success, derivation, message = self.parser.parse(tokens)

            print(f"🎯 Expected: {'SUCCESS' if expected_success else 'FAILURE'}")
            print(f"✅ Result: {'SUCCESS' if success else 'FAILURE'}")
            print(f"💬 Message: {message}")

            if success and len(derivation) > 0:
                print("📚 Parse derivation (first 5 steps):")
                for i, step in enumerate(derivation[:5]):
                    print(f"   {i+1}. {step}")
                if len(derivation) > 5:
                    print(f"   ... ({len(derivation) - 5} more steps)")

            # Check if result matches expectation
            test_passed = (success == expected_success)
            status = "✅ PASS" if test_passed else "❌ FAIL"
            print(f"🏆 Test Status: {status}")

            self.test_results.append({
                'name': test_name,
                'input': input_text,
                'expected': expected_success,
                'actual': success,
                'passed': test_passed,
                'message': message,
                'description': description
            })

            return test_passed

        except Exception as e:
            print(f"💥 Exception: {str(e)}")
            self.test_results.append({
                'name': test_name,
                'input': input_text,
                'expected': expected_success,
                'actual': False,
                'passed': False,
                'message': f"Exception: {str(e)}",
                'description': description
            })
            return False

    def run_all_tests(self):
        """Run all test cases from enhanced_grammar_test_cases.md"""
        print("🚀 Starting Vigorous Grammar Testing")
        print("=" * 60)

        # 1. NESTED EXPRESSION ASSIGNMENT TESTS ✅ NEW CAPABILITY
        print("\n🎯 CATEGORY 1: NESTED EXPRESSION ASSIGNMENT (NEW CAPABILITY)")
        self.run_test("1.1", "( ( A B + ) C )", True, "Basic nested assignment - assign (A + B) to C")
        self.run_test("1.2", "( ( ( X Y * ) Z + ) RESULT )", True, "Complex nested assignment - assign ((X * Y) + Z) to RESULT")
        self.run_test("1.3", "( ( 5.5 X ) TEMP )", True, "Memory storage within nested expression")

        # 2. ENHANCED BINARY OPERATIONS ✅ IMPROVED
        print("\n🎯 CATEGORY 2: ENHANCED BINARY OPERATIONS (IMPROVED)")
        self.run_test("2.1", "( ( A B + ) ( C D * ) - )", True, "Nested binary operations - (A + B) - (C * D)")
        self.run_test("2.2", "( ( ( A B + ) ( C D * ) - ) ( E F / ) + )", True, "Triple nesting with integer division")

        # 3. BACKWARD COMPATIBILITY ✅ MAINTAINED
        print("\n🎯 CATEGORY 3: BACKWARD COMPATIBILITY (MAINTAINED)")
        self.run_test("3.1", "( A B + )", True, "Standard RPN expression - unchanged")
        self.run_test("3.2", "( 42.0 VAR )", True, "Simple variable assignment - unchanged")
        self.run_test("3.3", "( X )", True, "Variable retrieval - unchanged")

        # 4. CONTROL STRUCTURES ✅ EXTENDED
        print("\n🎯 CATEGORY 4: CONTROL STRUCTURES (EXTENDED)")
        self.run_test("4.1", "( FOR 1 10 I ( ( I 2 % ) 0 == ) )", True, "FOR loop with nested modulo condition")
        self.run_test("4.2", "( WHILE ( ( X Y + ) 100 < ) ( ( X 1 + ) X ) )", True, "WHILE with complex nested test")
        self.run_test("4.3", "( IFELSE ( ( A B + ) C > ) ( ( A B + ) RESULT ) ( 0 RESULT ) )", True, "IFELSE with nested assignments")

        # 5. ERROR CASES ❌ SHOULD FAIL
        print("\n🎯 CATEGORY 5: ERROR CASES (SHOULD FAIL)")
        self.run_test("5.1", "( ( A B + C )", False, "Missing closing parenthesis")
        self.run_test("5.2", "( ( A + B ) C )", False, "Invalid prefix notation in expression")
        self.run_test("5.3", "( ( ) C )", False, "Empty nested expression")

        # 6. PDF DIVISION COMPLIANCE ✅ NEW PDF SPECIFICATION
        print("\n🎯 CATEGORY 6: PDF DIVISION COMPLIANCE (NEW SPECIFICATION)")
        self.run_test("6.1", "( A B | )", True, "Real division using pipe symbol (PDF compliant)")
        self.run_test("6.2", "( X Y / )", True, "Integer division using slash symbol (PDF compliant)")
        self.run_test("6.3", "( ( A B | ) RESULT )", True, "Real division in nested assignment")
        self.run_test("6.4", "( ( X Y / ) TEMP )", True, "Integer division in nested assignment")
        self.run_test("6.5", "( ( A B | ) ( C D / ) + )", True, "Mixed division types in complex expression")
        self.run_test("6.6", "( 42.5 6.5 | X )", True, "Real division with memory storage")
        self.run_test("6.7", "( 15 4 / Y )", True, "Integer division with memory storage")
        self.run_test("6.8a", "( X 2.0 | )", True, "Memory retrieval in real division")
        self.run_test("6.8b", "( Y 3 / )", True, "Memory retrieval in integer division")
        self.run_test("6.9", "( IFELSE ( ( A B | ) 5.0 > ) ( ( C D / ) RESULT ) ( 0 RESULT ) )", True, "Control structure with both division types")
        self.run_test("6.10", "( ( ( A B | ) ( C D / ) + ) ( ( E F | ) ( G H / ) - ) * )", True, "Maximum complexity with both divisions")

        # 7. EDGE CASES 🧪 STRESS TESTS
        print("\n🎯 CATEGORY 7: EDGE CASES (STRESS TESTS)")
        self.run_test("7.1", "( ( ( ( A B | ) C * ) ( D E / ) - ) F + )", True, "Maximum nesting depth with PDF divisions")
        self.run_test("7.2a", "( ( A B | ) C )", True, "Real division assignment for chained operations")
        self.run_test("7.2b", "( ( C 2 / ) FINAL )", True, "Integer division with memory result")
        self.run_test("7.3a", "( ( A B | ) ( C D / ) > )", True, "Real div + Integer div + Comparison")
        self.run_test("7.3b", "( ( X Y < ) ( Z W >= ) AND )", True, "Comparison + Logical operations")
        self.run_test("7.3c", "( ( P Q OR ) NOT )", True, "Logical operations")
        self.run_test("7.4", "( FOR 1 10 I ( ( ( I 2.0 | ) ( I 3 / ) + ) RESULT ) )", True, "Complex FOR loop with both division types")
        self.run_test("7.5", "( WHILE ( ( X 2.0 | ) 0.5 > ) ( ( X 3 / ) X ) )", True, "Nested WHILE with mixed divisions")

        # Generate final report
        self._generate_final_report()

    def run_real_world_tests(self, test_file_path: str = "/home/waifuisalie/Documents/pls_RA2/RA2_1/teste2.txt"):
        """Run real-world tests from teste2.txt file"""
        print("\n" + "=" * 80)
        print("🌍 REAL-WORLD TESTING SUITE")
        print("=" * 80)
        print(f"📁 Loading tests from: {test_file_path}")

        try:
            with open(test_file_path, 'r', encoding='utf-8') as f:
                lines = f.readlines()

            expressions = []
            for i, line in enumerate(lines, 1):
                line = line.strip()
                # Skip empty lines and comments
                if line and not line.startswith('#'):
                    # Remove inline comments
                    if '#' in line:
                        line = line.split('#')[0].strip()
                    if line:  # Make sure there's still content after removing comments
                        expressions.append((f"RW-{i:02d}", line, f"Real-world expression from line {i}"))

            print(f"📊 Found {len(expressions)} real-world expressions to test")

            # Test each expression
            passed = 0
            total = len(expressions)

            for test_name, expression, description in expressions:
                print(f"\n🔍 Testing: {test_name}")
                print(f"📝 Expression: {expression}")
                print(f"📋 Description: {description}")

                try:
                    # Tokenize
                    tokens = self.lexer.tokenize(expression)
                    print(f"🔤 Tokens: {[f'{t.type.value}({t.value})' for t in tokens if t.type != TokenType.FIM]}")

                    # Check for PDF division compliance
                    division_analysis = self._analyze_division_compliance(tokens)
                    if division_analysis:
                        print(f"📋 Division Analysis: {division_analysis}")

                    # Parse
                    success, derivation, message = self.parser.parse(tokens)

                    print(f"✅ Result: {'SUCCESS' if success else 'FAILURE'}")
                    print(f"💬 Message: {message}")

                    if success:
                        passed += 1
                        print("🏆 Test Status: ✅ PASS")
                    else:
                        print("🏆 Test Status: ❌ FAIL")

                    self.real_world_results.append({
                        'name': test_name,
                        'expression': expression,
                        'success': success,
                        'message': message,
                        'description': description,
                        'tokens': len([t for t in tokens if t.type != TokenType.FIM]),
                        'derivation_steps': len(derivation) if derivation else 0
                    })

                except Exception as e:
                    print(f"💥 Exception: {str(e)}")
                    print("🏆 Test Status: ❌ FAIL")
                    self.real_world_results.append({
                        'name': test_name,
                        'expression': expression,
                        'success': False,
                        'message': f"Exception: {str(e)}",
                        'description': description,
                        'tokens': 0,
                        'derivation_steps': 0
                    })

            # Generate real-world test report
            self._generate_real_world_report(passed, total)

        except FileNotFoundError:
            print(f"❌ ERROR: Test file not found: {test_file_path}")
        except Exception as e:
            print(f"❌ ERROR: Failed to load test file: {str(e)}")

    def _analyze_division_compliance(self, tokens: List[Token]) -> str:
        """Analyze PDF division compliance in tokens"""
        real_divisions = sum(1 for t in tokens if t.type == TokenType.DIVISAO_REAL)
        int_divisions = sum(1 for t in tokens if t.type == TokenType.DIVISAO_INTEIRA)

        if real_divisions == 0 and int_divisions == 0:
            return ""

        analysis = []
        if real_divisions > 0:
            analysis.append(f"Real divisions (|): {real_divisions}")
        if int_divisions > 0:
            analysis.append(f"Integer divisions (/): {int_divisions}")

        return " | ".join(analysis)

    def _generate_real_world_report(self, passed: int, total: int):
        """Generate real-world testing report"""
        print("\n" + "=" * 80)
        print("🌍 REAL-WORLD TESTING REPORT")
        print("=" * 80)

        success_rate = (passed / total * 100) if total > 0 else 0
        print(f"\n📊 REAL-WORLD RESULTS:")
        print(f"   Total Expressions: {total}")
        print(f"   Passed: ✅ {passed}")
        print(f"   Failed: ❌ {total - passed}")
        print(f"   Success Rate: {success_rate:.1f}%")

        # Analyze complexity
        if self.real_world_results:
            avg_tokens = sum(r['tokens'] for r in self.real_world_results) / len(self.real_world_results)
            max_tokens = max(r['tokens'] for r in self.real_world_results)
            avg_derivation = sum(r['derivation_steps'] for r in self.real_world_results) / len(self.real_world_results)

            print(f"\n📈 COMPLEXITY ANALYSIS:")
            print(f"   Average tokens per expression: {avg_tokens:.1f}")
            print(f"   Maximum tokens in expression: {max_tokens}")
            print(f"   Average derivation steps: {avg_derivation:.1f}")

        # Division compliance analysis
        division_expressions = [r for r in self.real_world_results if 'division' in r['description'].lower() or '|' in r['expression'] or '/' in r['expression']]
        if division_expressions:
            division_passed = sum(1 for r in division_expressions if r['success'])
            print(f"\n🔍 PDF DIVISION COMPLIANCE:")
            print(f"   Division expressions: {len(division_expressions)}")
            print(f"   Division tests passed: {division_passed}/{len(division_expressions)}")

        # Failed tests details
        failed_tests = [r for r in self.real_world_results if not r['success']]
        if failed_tests:
            print(f"\n❌ FAILED REAL-WORLD TESTS:")
            for result in failed_tests[:5]:  # Show first 5 failures
                print(f"   🔸 {result['name']}: {result['message']}")
                print(f"      Expression: {result['expression']}")

        print("=" * 80)

    def run_comprehensive_testing(self, test_file_path: str = "/home/waifuisalie/Documents/pls_RA2/RA2_1/teste2.txt"):
        """Run both vigorous and real-world tests"""
        print("🔥 COMPREHENSIVE GRAMMAR TESTING SUITE")
        print("Testing Updated_LL1_Grammar_PDF_Compliant.md with Enhanced Real-World Scenarios")
        print("=" * 80)

        # Run original vigorous tests
        self.run_all_tests()

        # Run real-world tests
        self.run_real_world_tests(test_file_path)

        # Generate combined report
        self._generate_comprehensive_report()

    def _generate_comprehensive_report(self):
        """Generate comprehensive testing report combining both test suites"""
        print("\n" + "=" * 80)
        print("🏆 COMPREHENSIVE TESTING - FINAL REPORT")
        print("=" * 80)

        # Original test results
        total_original = len(self.test_results)
        passed_original = sum(1 for result in self.test_results if result['passed'])

        # Real-world test results
        total_real_world = len(self.real_world_results)
        passed_real_world = sum(1 for result in self.real_world_results if result['success'])

        # Combined results
        total_combined = total_original + total_real_world
        passed_combined = passed_original + passed_real_world

        print(f"\n📊 COMPREHENSIVE RESULTS:")
        print(f"   Original Vigorous Tests: {passed_original}/{total_original} ({(passed_original/total_original)*100:.1f}%)")
        print(f"   Real-World Tests: {passed_real_world}/{total_real_world} ({(passed_real_world/total_real_world)*100:.1f}%)")
        print(f"   📈 TOTAL COMBINED: {passed_combined}/{total_combined} ({(passed_combined/total_combined)*100:.1f}%)")

        # Final verdict
        print(f"\n🏆 FINAL COMPREHENSIVE VERDICT:")
        if passed_combined == total_combined:
            print(f"   🎉 GRAMMAR IS FULLY PRODUCTION READY!")
            print(f"   ✅ All {total_combined} test cases passed")
            print(f"   ✅ Vigorous theoretical validation complete")
            print(f"   ✅ Real-world practical validation complete")
            print(f"   ✅ PDF compliance verified in real scenarios")
            print(f"   ✅ Enhanced features validated in practice")
        elif passed_combined >= total_combined * 0.95:
            print(f"   ⚠️  GRAMMAR NEARLY READY - Minor real-world issues detected")
            print(f"   📊 {passed_combined}/{total_combined} tests passed ({(passed_combined/total_combined)*100:.1f}%)")
        else:
            print(f"   ❌ GRAMMAR NEEDS IMPROVEMENTS FOR REAL-WORLD USE")
            print(f"   📊 {passed_combined}/{total_combined} tests passed ({(passed_combined/total_combined)*100:.1f}%)")

        print("=" * 80)

    def _generate_final_report(self):
        """Generate comprehensive test results report"""
        print("\n" + "=" * 80)
        print("🏆 VIGOROUS GRAMMAR TESTING - FINAL REPORT")
        print("=" * 80)

        total_tests = len(self.test_results)
        passed_tests = sum(1 for result in self.test_results if result['passed'])
        failed_tests = total_tests - passed_tests

        print(f"\n📊 OVERALL RESULTS:")
        print(f"   Total Tests: {total_tests}")
        print(f"   Passed: ✅ {passed_tests}")
        print(f"   Failed: ❌ {failed_tests}")
        print(f"   Success Rate: {(passed_tests/total_tests)*100:.1f}%")

        # Category breakdown
        categories = {
            "Nested Assignment": ["1.1", "1.2", "1.3"],
            "Enhanced Binary Ops": ["2.1", "2.2"],
            "Backward Compatibility": ["3.1", "3.2", "3.3"],
            "Control Structures": ["4.1", "4.2", "4.3"],
            "Error Handling": ["5.1", "5.2", "5.3"],
            "PDF Division Compliance": ["6.1", "6.2", "6.3", "6.4", "6.5", "6.6", "6.7", "6.8a", "6.8b", "6.9", "6.10"],
            "Edge Cases": ["7.1", "7.2a", "7.2b", "7.3a", "7.3b", "7.3c", "7.4", "7.5"]
        }

        print(f"\n📋 CATEGORY BREAKDOWN:")
        for category, test_ids in categories.items():
            category_results = [r for r in self.test_results if any(r['name'].startswith(tid) for tid in test_ids)]
            category_passed = sum(1 for r in category_results if r['passed'])
            category_total = len(category_results)
            status = "✅" if category_passed == category_total else "⚠️"
            print(f"   {status} {category}: {category_passed}/{category_total}")

        # Failed tests details
        if failed_tests > 0:
            print(f"\n❌ FAILED TESTS DETAILS:")
            for result in self.test_results:
                if not result['passed']:
                    print(f"   🔸 {result['name']}: {result['message']}")
                    print(f"      Input: {result['input']}")
                    print(f"      Expected: {'SUCCESS' if result['expected'] else 'FAILURE'}")
                    print(f"      Actual: {'SUCCESS' if result['actual'] else 'FAILURE'}")

        # PDF Compliance specific report
        pdf_tests = [r for r in self.test_results if r['name'].startswith('6.')]
        pdf_passed = sum(1 for r in pdf_tests if r['passed'])
        pdf_total = len(pdf_tests)

        print(f"\n🔍 PDF DIVISION COMPLIANCE ANALYSIS:")
        print(f"   📊 PDF Tests: {pdf_passed}/{pdf_total} passed")
        if pdf_passed == pdf_total:
            print(f"   ✅ FULL PDF COMPLIANCE ACHIEVED!")
            print(f"   🎯 Real division (|) and Integer division (/) working correctly")
        else:
            print(f"   ⚠️  PDF compliance issues detected")

        # Enhancement capability report
        enhancement_tests = [r for r in self.test_results if r['name'].startswith('1.')]
        enhancement_passed = sum(1 for r in enhancement_tests if r['passed'])
        enhancement_total = len(enhancement_tests)

        print(f"\n🚀 NESTED ASSIGNMENT ENHANCEMENT ANALYSIS:")
        print(f"   📊 Enhancement Tests: {enhancement_passed}/{enhancement_total} passed")
        if enhancement_passed == enhancement_total:
            print(f"   ✅ REVOLUTIONARY NESTED ASSIGNMENT CAPABILITY CONFIRMED!")
            print(f"   🎯 ( ( EXPR ) VAR ) pattern working perfectly")
        else:
            print(f"   ⚠️  Enhancement capability issues detected")

        # Final verdict
        print(f"\n🏆 FINAL VERDICT:")
        if passed_tests == total_tests:
            print(f"   🎉 GRAMMAR IS PRODUCTION READY!")
            print(f"   ✅ All test cases passed")
            print(f"   ✅ PDF compliance verified")
            print(f"   ✅ Enhanced capabilities confirmed")
            print(f"   ✅ Backward compatibility maintained")
        elif passed_tests >= total_tests * 0.9:
            print(f"   ⚠️  GRAMMAR MOSTLY READY - Minor issues detected")
        else:
            print(f"   ❌ GRAMMAR NEEDS SIGNIFICANT IMPROVEMENTS")

        print("=" * 80)

def main():
    """Main test execution"""
    print("🔥 COMPREHENSIVE LL(1) GRAMMAR TESTING SUITE")
    print("Testing Updated_LL1_Grammar_PDF_Compliant.md with Enhanced Real-World Scenarios")
    print("=" * 80)

    runner = GrammarTestRunner()

    # Option to run comprehensive tests (both vigorous + real-world)
    import sys
    if len(sys.argv) > 1 and sys.argv[1] == "--comprehensive":
        runner.run_comprehensive_testing()
    elif len(sys.argv) > 1 and sys.argv[1] == "--real-world":
        runner.run_real_world_tests()
    else:
        # Default: run original vigorous tests only
        print("🎯 Running Original Vigorous Tests")
        print("💡 Use --comprehensive for both test suites or --real-world for real-world tests only")
        print("=" * 80)
        runner.run_all_tests()

if __name__ == "__main__":
    main()