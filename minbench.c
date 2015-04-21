#include <stdint.h>
#include <stdio.h>
#include <string.h>
#include <x86intrin.h>
#include <emmintrin.h>
void unshuffle(size_t bytesoftype, size_t blocksize,
               const uint8_t* _src, uint8_t* _dest);

#define N 1024
#define tm 1
#define NIT 1000000
int main()
{
    double * s = _mm_malloc(N * 8 + 4, 32);
    double * d = _mm_malloc(N * 8 + 4, 32);
    double * d2 = _mm_malloc(N * 8 + 4, 32);
    memset(s, 0, N*8);
    memset(d, 0, N*8);
    memset(d2, 0, N*8);
    unsigned long long min = -1;
    int o;
    o = 0;
    printf("%ld\n", (long)&d[o] % 32);
    for (int i = 0; i < NIT; i++) {
        long long ts = __rdtsc();
        unshuffle(sizeof(d[0]) * tm, N / tm, (uint8_t*)&s[o], (uint8_t*)&d[o]);
        long long nt = __rdtsc();
        if (nt - ts < min)
            min = nt - ts;
    }
    printf("%llu\n", min);
    min = -1;

    o = 2;
    printf("%ld\n", (long)&d[o] % 32);
    for (int i = 0; i < NIT; i++) {
        long long ts = __rdtsc();
        unshuffle(sizeof(d[0]) * tm, N / tm, (uint8_t*)&s[o], (uint8_t*)&d2[o]);
        long long nt = __rdtsc();
        if (nt - ts < min)
            min = nt - ts;
    }
    printf("%llu\n", min);
    printf("%d\n", memcmp(d, &d2[o], 8*N));
}
