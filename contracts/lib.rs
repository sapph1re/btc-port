use anchor_lang::prelude::*;

declare_id!("");

#[account]
pub struct TransactionData {
    pub user_address: String,
    pub tx_hash: String,
    pub amount: u64,
    pub is_incoming: bool,
}

#[account]
pub struct BitcoinTransactionProcessor {
    pub oracle_authority: Pubkey,
    pub transactions: Vec<String>,
    pub transaction_data: Vec<TransactionData>,
}

#[derive(Accounts)]
pub struct Initialize<'info> {
    #[account(init, payer = owner, space = 8 + 8)]
    pub processor: Account<'info, BitcoinTransactionProcessor>,
    #[account(mut)]
    pub owner: Signer<'info>,
    pub system_program: Program<'info, System>,
}

pub fn init(ctx: Context<Initialize>) -> Result<()> {
    let processor = &mut ctx.accounts.processor;
    processor.oracle_authority = Pubkey::default();
    processor.transactions = vec![];
    processor.transaction_data = vec![];
    Ok(())
}

#[derive(Accounts)]
pub struct SetOracleAuthority<'info> {
    #[account(mut)]
    pub processor: Account<'info, BitcoinTransactionProcessor>,
    pub owner: Signer<'info>,
}

pub fn set_oracle_authority(
    ctx: Context<SetOracleAuthority>,
    oracle_authority: Pubkey,
) -> Result<()> {
    let account_info = ctx.accounts.processor.to_account_info();
    let processor = &mut ctx.accounts.processor;
    require!(
        *account_info.owner == ctx.accounts.owner.key(),
        ErrorCode::InvalidOwner
    );
    processor.oracle_authority = oracle_authority;
    Ok(())
}

#[derive(Accounts)]
pub struct AddTransaction<'info> {
    #[account(mut)]
    pub processor: Account<'info, BitcoinTransactionProcessor>,
    pub oracle_authority: Signer<'info>,
}

pub fn add_transaction(
    ctx: Context<AddTransaction>,
    user_address: String,
    tx_hash: String,
    amount: u64,
    is_incoming: bool,
) -> Result<()> {
    let processor = &mut ctx.accounts.processor;
    require!(
        ctx.accounts.oracle_authority.key() == processor.oracle_authority,
        ErrorCode::InvalidOracleAuthority
    );
    require!(
        !processor.transactions.contains(&tx_hash),
        ErrorCode::TransactionAlreadyProcessed
    );

    let transaction = TransactionData {
        user_address,
        tx_hash: tx_hash.clone(), // Clone the tx_hash value
        amount,
        is_incoming,
    };
    processor.transaction_data.push(transaction);
    processor.transactions.push(tx_hash); // Use the original tx_hash value here
    Ok(())
}

#[derive(Accounts)]
pub struct GetAllTransactions<'info> {
    #[account(mut)]
    pub processor: Account<'info, BitcoinTransactionProcessor>,
}

pub fn get_all_transactions(ctx: Context<GetAllTransactions>) -> Vec<TransactionData> {
    ctx.accounts.processor.transaction_data.clone()
}

#[error_code]
pub enum ErrorCode {
    #[msg("Invalid owner")]
    InvalidOwner,
    #[msg("Invalid oracle authority")]
    InvalidOracleAuthority,
    #[msg("Transaction already processed")]
    TransactionAlreadyProcessed,
}
