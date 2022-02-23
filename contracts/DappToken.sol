// SPDX-License-Identifier: MIT

pragma solidity ^0.8.0;

import "@openzeppelin/contracts/token/ERC20/ERC20.sol";

contract KCToken is ERC20 {
    constructor() ERC20("KC Token", "KC") {
        _mint(msg.sender, 1000000000000000000000000);
    }
}
