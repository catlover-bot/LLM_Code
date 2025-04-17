以下は、1以上100以下の自然数のうち、素数を判定して出力するC言語のサンプルコードです。  
実行すると、2, 3, 5, 7, 11, 13 … 97 のように、100以内の素数が出力されます。
--------------------------------------------------------------------------------
#include <stdio.h>
#include <math.h>
#include <stdbool.h>
int main(void) {
    for(int num = 2; num <= 100; num++) {
        bool isPrime = true;  
        for(int div = 2; div <= (int)sqrt(num); div++) {
            if(num % div == 0) {
                isPrime = false;
                break;
            }
        if(isPrime) {
            printf("%d ", num);
    printf("\n");
    return 0;
■ コードのポイント
1. num を 2 から 100 までループ。1 は素数とはみなさないため 2 からスタートしています。  
2. isPrime というフラグ変数を使い、割り切れるかどうかをチェックします。  
3. sqrt(num) まで割り算を行い、割り切れたら素数ではないと判断します。  
4. 素数と判定できた数だけを出力します。