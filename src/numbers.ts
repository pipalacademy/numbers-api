/**
 * Numbers library.
 */

export function fibs(a: number, b: number, n: number): number[] {
  const result = [];
  for (let i = 0; i < n; i++) {
    result.push(a);
    [a, b] = [b, a + b];
  }
  return result;
}

export function product(numbers: number[]): number {
  return numbers.reduce((result, n) => result * n, 1);
}
