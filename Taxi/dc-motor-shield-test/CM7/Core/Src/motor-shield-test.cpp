#include "main.h"
void glow(volatile uint32_t* channel, GPIO_TypeDef* port_A, GPIO_TypeDef* port_B, uint16_t pin_A, uint16_t pin_B){
	  HAL_GPIO_WritePin(port_A, pin_A, GPIO_PIN_SET);
	  while((*channel) < 300){
		  (*channel) ++;
		  HAL_Delay(1);
	  }
	  while(*channel > 0){
		  (*channel) --;
		  HAL_Delay(1);
	  }
	  HAL_GPIO_TogglePin(port_A, pin_A);
	  HAL_GPIO_TogglePin(port_B, pin_B);
	  while((*channel) < 300){
		  (*channel) ++;
		  HAL_Delay(1);
	  }
	  while(*channel > 0){
		  (*channel) --;
		  HAL_Delay(1);
	  }
	  (*channel) = 0;

	  HAL_GPIO_WritePin(port_B, pin_B, GPIO_PIN_RESET);
}
void setup(){
	extern TIM_HandleTypeDef htim1;
	HAL_TIM_PWM_Start(&htim1, TIM_CHANNEL_1);
	HAL_TIM_PWM_Start(&htim1, TIM_CHANNEL_2);
	HAL_TIM_PWM_Start(&htim1, TIM_CHANNEL_3);
	HAL_TIM_PWM_Start(&htim1, TIM_CHANNEL_4);

}
void loop(){
	glow(&TIM1->CCR1, MA_DIRA_GPIO_Port, MA_DIRB_GPIO_Port, MA_DIRA_Pin, MA_DIRB_Pin);
	glow(&TIM1->CCR2, MB_DIRA_GPIO_Port, MB_DIRB_GPIO_Port, MB_DIRA_Pin, MB_DIRB_Pin);
	glow(&TIM1->CCR3, MC_DIRA_GPIO_Port, MC_DIRB_GPIO_Port, MC_DIRA_Pin, MC_DIRB_Pin);
	glow(&TIM1->CCR4, MD_DIRA_GPIO_Port, MD_DIRB_GPIO_Port, MD_DIRA_Pin, MD_DIRB_Pin);
}
