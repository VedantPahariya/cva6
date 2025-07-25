/*
 * Vector Intrinsics Test using RISC-V Vector Extension
 * This test uses actual RISC-V vector intrinsics
 */

#include <stdint.h>
#include <riscv_vector.h>

#define ARRAY_SIZE 16

// Test data
int32_t input_a[ARRAY_SIZE] = {1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12, 13, 14, 15, 16};
int32_t input_b[ARRAY_SIZE] = {16, 15, 14, 13, 12, 11, 10, 9, 8, 7, 6, 5, 4, 3, 2, 1};
int32_t result[ARRAY_SIZE];
int32_t expected[ARRAY_SIZE] = {17, 17, 17, 17, 17, 17, 17, 17, 17, 17, 17, 17, 17, 17, 17, 17};

// Vector addition using RISC-V vector intrinsics
void vector_add_intrinsics(int32_t* dst, const int32_t* src1, const int32_t* src2, size_t n) {
    size_t vl;
    
    for (size_t i = 0; i < n; ) {
        // Set vector length for this iteration
        vl = __riscv_vsetvl_e32m1(n - i);
        
        // Load vectors
        vint32m1_t va = __riscv_vle32_v_i32m1(src1 + i, vl);
        vint32m1_t vb = __riscv_vle32_v_i32m1(src2 + i, vl);
        
        // Perform vector addition
        vint32m1_t vc = __riscv_vadd_vv_i32m1(va, vb, vl);
        
        // Store result
        __riscv_vse32_v_i32m1(dst + i, vc, vl);
        
        i += vl;
    }
}

// Vector multiplication and accumulation
int32_t vector_dot_product(const int32_t* src1, const int32_t* src2, size_t n) {
    int32_t sum = 0;
    size_t vl;
    vint32m1_t vsum = __riscv_vmv_v_x_i32m1(0, 1);
    
    for (size_t i = 0; i < n; ) {
        vl = __riscv_vsetvl_e32m1(n - i);
        
        vint32m1_t va = __riscv_vle32_v_i32m1(src1 + i, vl);
        vint32m1_t vb = __riscv_vle32_v_i32m1(src2 + i, vl);
        
        // Multiply and accumulate
        vsum = __riscv_vmacc_vv_i32m1(vsum, va, vb, vl);
        
        i += vl;
    }
    
    // Reduce to scalar
    vint32m1_t vzero = __riscv_vmv_v_x_i32m1(0, 1);
    vint32m1_t vres = __riscv_vredsum_vs_i32m1_i32m1(vsum, vzero, __riscv_vsetvl_e32m1(n));
    
    return __riscv_vmv_x_s_i32m1_i32(vres);
}

// Test vector addition
int test_vector_addition() {
    vector_add_intrinsics(result, input_a, input_b, ARRAY_SIZE);
    
    for (int i = 0; i < ARRAY_SIZE; i++) {
        if (result[i] != expected[i]) {
            return 1; // Fail
        }
    }
    
    return 0; // Pass
}

// Test dot product
int test_dot_product() {
    int32_t dot_result = vector_dot_product(input_a, input_b, ARRAY_SIZE);
    int32_t expected_dot = 1496; // Pre-calculated expected result
    
    return (dot_result == expected_dot) ? 0 : 1;
}

// Vector configuration test
int test_vector_config() {
    // Test setting different vector lengths
    size_t vl1 = __riscv_vsetvl_e32m1(8);
    size_t vl2 = __riscv_vsetvl_e32m2(16);
    size_t vl3 = __riscv_vsetvl_e32m4(32);
    
    // Basic sanity checks
    if (vl1 == 0 || vl2 == 0 || vl3 == 0) {
        return 1; // Fail
    }
    
    return 0; // Pass
}

int main() {
    int result = 0;
    
    // Test vector addition
    if (test_vector_addition() != 0) {
        result = 1;
    }
    
    // Test dot product
    if (test_dot_product() != 0) {
        result = 1;
    }
    
    // Test vector configuration
    if (test_vector_config() != 0) {
        result = 1;
    }
    
    return result;
}
