// Simple Vector Test Program for CVA6+ARA Integration
// This program uses RISC-V vector intrinsics to test vector operations

#include <stdio.h>

// Include RISC-V vector intrinsics
#ifdef __riscv_vector
#include <riscv_vector.h>
#endif

#define ARRAY_SIZE 16

// Test data
float a[ARRAY_SIZE] = {1.0, 2.0, 3.0, 4.0, 5.0, 6.0, 7.0, 8.0,
                       9.0, 10.0, 11.0, 12.0, 13.0, 14.0, 15.0, 16.0};
float b[ARRAY_SIZE] = {1.0, 1.0, 1.0, 1.0, 1.0, 1.0, 1.0, 1.0,
                       1.0, 1.0, 1.0, 1.0, 1.0, 1.0, 1.0, 1.0};
float c[ARRAY_SIZE];

// Scalar version (fallback)
void vector_add_scalar(float *a, float *b, float *c, int n) {
    for (int i = 0; i < n; i++) {
        c[i] = a[i] + b[i];
    }
}

#ifdef __riscv_vector
// Vector version using intrinsics
void vector_add_intrinsic(float *a, float *b, float *c, size_t n) {
    size_t vl;
    for (size_t i = 0; i < n; i += vl) {
        vl = __riscv_vsetvl_e32m1(n - i);
        vfloat32m1_t va = __riscv_vle32_v_f32m1(a + i, vl);
        vfloat32m1_t vb = __riscv_vle32_v_f32m1(b + i, vl);
        vfloat32m1_t vc = __riscv_vfadd_vv_f32m1(va, vb, vl);
        __riscv_vse32_v_f32m1(c + i, vc, vl);
    }
}

// Auto-vectorizable version
void vector_add_auto(float *a, float *b, float *c, int n) {
    #pragma GCC ivdep
    for (int i = 0; i < n; i++) {
        c[i] = a[i] + b[i];
    }
}
#endif

void print_array(const char* name, float *arr, int n) {
    printf("%s: ", name);
    for (int i = 0; i < n; i++) {
        printf("%.1f ", arr[i]);
    }
    printf("\n");
}

int main() {
    printf("CVA6+ARA Vector Test Program\n");
    printf("============================\n");
    
    print_array("Array A", a, ARRAY_SIZE);
    print_array("Array B", b, ARRAY_SIZE);
    
#ifdef __riscv_vector
    printf("\nTesting with RISC-V Vector Extensions:\n");
    
    // Test intrinsic version
    vector_add_intrinsic(a, b, c, ARRAY_SIZE);
    print_array("Result (intrinsic)", c, ARRAY_SIZE);
    
    // Clear result array
    for (int i = 0; i < ARRAY_SIZE; i++) c[i] = 0.0;
    
    // Test auto-vectorized version
    vector_add_auto(a, b, c, ARRAY_SIZE);
    print_array("Result (auto-vec)", c, ARRAY_SIZE);
#else
    printf("\nVector extensions not available, using scalar version:\n");
    vector_add_scalar(a, b, c, ARRAY_SIZE);
    print_array("Result (scalar)", c, ARRAY_SIZE);
#endif
    
    // Verify results
    int success = 1;
    for (int i = 0; i < ARRAY_SIZE; i++) {
        if (c[i] != a[i] + b[i]) {
            success = 0;
            break;
        }
    }
    
    printf("\nTest %s!\n", success ? "PASSED" : "FAILED");
    return success ? 0 : 1;
}
