import {PaymentMethod} from '@lavka/api-typings/uservices/grocery-api/definitions'

interface Props {
  responseNativePaymentMethods: PaymentMethod[]
  responseNativeLastUsedPaymentMethod: PaymentMethod | null
}

export const makeMockServerResponseData = (props: Props) => {
  return {mockServerDataJSON: JSON.stringify(props)}
}
