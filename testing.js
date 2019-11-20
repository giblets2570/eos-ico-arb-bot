
let Web3 = require('web3');
let web3 = new Web3('https://kovan.infura.io/VB6w0UngxVr7YK5Zkatv')

let transactions = [
	"0x78b3ea80a22de582903dfdca5f18961c55b1ff5016acaa94e0ef8d4f52233081", // Doesn't work
	"0xcd0325117d990917a0bc0b96a9a25008b6a9b33648ae9e314e6eb340548d4e35" // Works
]

const InputDataDecoder = require('ethereum-input-data-decoder');
const decoder = new InputDataDecoder(`${__dirname}/contract-abi.json`);

transactions.map((txHash, number) => {
	web3.eth.getTransaction(txHash, (error, txResult) => {
		console.log(txResult);
		const result = decoder.decodeData(txResult.input);
		console.log(`${number}: ${JSON.stringify(result)}`);
	});
})
