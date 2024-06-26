use anchor_lang::prelude::*;

declare_id!("");

#[program]
pub mod store_transactions {
    use super::*;

    pub fn init(ctx: Context<Initialize>) -> Result<()> {
        let processor = &mut ctx.accounts.processor;
        processor.owner = ctx.accounts.owner.key();
        processor.oracle_authority = Pubkey::default();
        processor.transactions = vec![];
        processor.transaction_data = vec![];
        Ok(())
    }

    pub fn set_oracle_authority(
        ctx: Context<SetOracleAuthority>,
        oracle_authority: Pubkey,
    ) -> Result<()> {
        let processor = &mut ctx.accounts.processor;
        require!(
            processor.owner == ctx.accounts.owner.key(),
            ErrorCode::InvalidOwner
        );
        processor.oracle_authority = oracle_authority;
        Ok(())
    }

    pub fn add_transaction(
        ctx: Context<AddTransaction>,
        asset: String,
        user_address: String,
        tx_hash: String,
        amount: u64,
        is_incoming: bool,
        block: u32,
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
            asset,
            user_address,
            tx_hash: tx_hash.clone(),
            amount,
            is_incoming,
            block,
        };
        processor.transaction_data.push(transaction);
        processor.transactions.push(tx_hash);
        Ok(())
    }
}

#[derive(Accounts)]
pub struct Initialize<'info> {
    #[account(
        init,
        payer = owner,
        space = 8 + 8 + 8 * 32 + 8 * 32,
        seeds = [b"processor"],
        bump
    )]
    pub processor: Account<'info, BitcoinTransactionProcessor>,
    #[account(mut)]
    pub owner: Signer<'info>,
    pub system_program: Program<'info, System>,
}

#[derive(Accounts)]
pub struct SetOracleAuthority<'info> {
    #[account(mut)]
    pub processor: Account<'info, BitcoinTransactionProcessor>,
    pub owner: Signer<'info>,
}

#[derive(Accounts)]
pub struct AddTransaction<'info> {
    #[account(mut)]
    pub processor: Account<'info, BitcoinTransactionProcessor>,
    pub oracle_authority: Signer<'info>,
}

#[account]
#[derive(Default)]
pub struct BitcoinTransactionProcessor {
    pub owner: Pubkey,
    pub oracle_authority: Pubkey,
    pub transactions: Vec<String>,
    pub transaction_data: Vec<TransactionData>,
}

#[derive(AnchorSerialize, AnchorDeserialize, Clone, Default)]
pub struct TransactionData {
    pub asset: String,
    pub user_address: String,
    pub tx_hash: String,
    pub amount: u64,
    pub is_incoming: bool,
    pub block: u32,
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
