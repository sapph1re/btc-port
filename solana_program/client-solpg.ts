import { PublicKey } from "@solana/web3.js";
import { AnchorError } from "@project-serum/anchor";

console.log(pg.PROGRAM_ID.toString());
console.log("My address:", pg.wallet.publicKey.toString());
const balance = await pg.connection.getBalance(pg.wallet.publicKey);
console.log(`My balance: ${balance / web3.LAMPORTS_PER_SOL} SOL`);

const processorAccountPda = PublicKey.findProgramAddressSync(
  [Buffer.from("processor")],
  pg.PROGRAM_ID
);

// Fetch processor account to check if it's already initialized
try {
  const processorAccount =
    await pg.program.account.bitcoinTransactionProcessor.fetch(
      processorAccountPda[0]
    );
  console.log("Processor already initialized.");
} catch (err) {
  // If fetching the account fails, it likely means the account is not yet initialized
  console.log("Initializing processor...");
  const initTxHash = await pg.program.methods
    .init()
    .accounts({
      processor: processorAccountPda[0],
      owner: pg.wallet.publicKey,
      systemProgram: web3.SystemProgram.programId,
    })
    .rpc();
  await logTransaction(initTxHash);
}

console.log("Setting oracle authority...");
const setOracleAuthorityTxHash = await pg.program.methods
  .setOracleAuthority(pg.wallet.publicKey)
  .accounts({
    processor: processorAccountPda[0],
    owner: pg.wallet.publicKey,
  })
  .rpc();
await logTransaction(setOracleAuthorityTxHash);

await loadAndPrintTransactions();

console.log("Adding transaction...");
try {
  const addTxHash = await pg.program.methods
    .addTransaction("user-address", "tx-hash", new BN(1234), true)
    .accounts({
      processor: processorAccountPda[0],
      oracleAuthority: pg.wallet.publicKey,
    })
    .rpc();
  await logTransaction(addTxHash);
} catch (err) {
  if (err.error.errorCode.code == "TransactionAlreadyProcessed") {
    console.log("Transaction already processed. Skipping...");
  } else {
    console.error("Error adding transaction:", err);
    throw err;
  }
}

await loadAndPrintTransactions();

async function loadAndPrintTransactions() {
  console.log("Loading stored transactions...");
  const processorAccount =
    await pg.program.account.bitcoinTransactionProcessor.fetch(
      processorAccountPda[0]
    );

  console.log("Stored transactions:");
  for (const transaction of processorAccount.transactionData) {
    console.log(
      ` - user address: ${transaction.userAddress}, tx: ${
        transaction.txHash
      }, amount: ${transaction.amount.toNumber()}, incoming: ${
        transaction.isIncoming
      }`
    );
  }
  console.log("---");
}

async function logTransaction(txHash) {
  const { blockhash, lastValidBlockHeight } =
    await pg.connection.getLatestBlockhash();
  await pg.connection.confirmTransaction({
    blockhash,
    lastValidBlockHeight,
    signature: txHash,
  });
  console.log(
    `Transaction sent: https://explorer.solana.com/tx/${txHash}?cluster=devnet`
  );
}
